import os
import sys
import re
import csv
import argparse
import nltk
import string
from multiprocessing import Process
from tqdm import tqdm
from lib.utils import stage_item_count
from config import cfg

def parse_args():
    parser = argparse.ArgumentParser(description='alt cleaner')
    parser.add_argument('--src', type=str, default='gif_alt_info_clean')
    parser.add_argument("--dst", type=str, default='gif_alt_info_clean_0')
    parser.add_argument("--num_worker", type=int, default=4)
    parser.add_argument("--backend", type=str, default='spacy')
    parser.add_argument("--remove_punc", action='store_true')

    args = parser.parse_args()
    assert 0 < args.num_worker
    assert args.backend in ['spacy', 'nltk']
    return args

args = parse_args()

def unique_whitespace(sent):
    return re.sub(' +', ' ', sent)

def remove_punc(sent):
    tokens = sent.split()
    tokens = [w for w in tokens if not w in string.punctuation]
    new_sent = ' '.join(tokens)
    return new_sent

def generate_pos_tag(wid, infile, outfile, total, backend):
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']
    reader = csv.DictReader(open(infile, 'r', encoding='utf-8'), delimiter='\t')
    writer = csv.DictWriter(open(outfile, 'w', encoding='utf-8', newline=''), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    if backend == 'spacy':
        # lazy load spacy model
        import spacy
        import en_core_web_lg
        nlp = spacy.load("en_core_web_lg", disable=["parser", "ner"])
        def spacy_pos_tag(text):
            tokens = text.split()
            spaces = [True] * (len(tokens) - 1) + [False]

            doc = spacy.tokens.doc.Doc(
                nlp.vocab, words=tokens, spaces=spaces)
            for name, proc in nlp.pipeline:
                doc = proc(doc)

            pos_tags = [
                (token.text, token.tag_) \
                for token in doc
            ]
            return pos_tags

    with tqdm(total=total, ascii=True) as pbar:
        for row in reader:
            gid = row['gid']
            uid = row['uid']
            gifUrl = row['gifUrl']
            title = row['title'].strip().lower()
            alt = row['alt'].strip().lower()

            title = unique_whitespace(title)
            alt = unique_whitespace(alt)
            
            if args.remove_punc:
                title = remove_punc(title)
                alt = remove_punc(alt)

            if len(title) == 0:
                title = 'none'
            if backend == 'nltk':
                title_pos = nltk.pos_tag(title.split())
            elif backend == 'spacy':
                title_pos = spacy_pos_tag(title)
            else:
                raise NotImplementedError
            title_pos = [pos[1] for pos in title_pos]
            title_pos = '\t'.join(title_pos)

            if len(alt) == 0:
                alt = 'none'
            if backend == 'nltk':
                alt_pos = nltk.pos_tag(alt.split())
            elif backend == 'spacy':
                alt_pos = spacy_pos_tag(alt)
            else:
                raise NotImplementedError
            alt_pos = [pos[1] for pos in alt_pos]
            alt_pos = '\t'.join(alt_pos)
            
            if title != 'none' or alt != 'none':
                writer.writerow({'gid': gid, 'uid': uid, 'gifUrl': gifUrl, 'title': title,
                                'title_pos': title_pos, 'alt': alt, 'alt_pos': alt_pos })

            pbar.update(1)


if __name__ == '__main__':
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos', 'alt', 'alt_pos']

    print("========== Stage 2 %s Pos_Tags ==========" % args.backend.upper())

    # split data
    reader = csv.DictReader(open(os.path.join('result', args.src + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
    split_files = [os.path.join('result', 'split' + str(wid) + '.csv') for wid in range(args.num_worker)]

    split_fieldnames = ['gid', 'uid','gifUrl', 'title', 'alt']
    fids = [open(file, 'w', encoding='utf-8', newline='') for file in split_files]
    writers = [csv.DictWriter(fid, fieldnames=split_fieldnames, delimiter='\t') for fid in fids]
    for w in writers:
        w.writeheader()

    totals = {}
    for gid, row in enumerate(reader):
        uid = row['uid']
        gifUrl = row['gifUrl']
        title = row['title'].strip().lower()
        alt = row['alt'].strip().lower()

        wid = gid % args.num_worker
        writers[wid].writerow({ 'gid': cfg.BASE_GID + gid, 'uid': uid, 'gifUrl': gifUrl, 'title': title, 'alt': alt })
        totals[wid] = totals.get(wid, 0) + 1

    for f in fids:
        f.close()

    # split and run multi process
    procs = []
    outfiles = []
    for w_id, infile in enumerate(split_files):
        outfile = os.path.join('result', 'temp' + str(w_id) + '.csv')
        p = Process(target=generate_pos_tag,
                    args=(w_id, infile, outfile, totals[w_id], args.backend))
        p.daemon = True
        p.start()
        procs.append(p)
        outfiles.append(outfile)

    for p in procs:
        p.join()

    # grab and merge the internal result
    print("Merge result...")
    writer = csv.DictWriter(open(os.path.join('result', args.dst + '.csv'), 'w', encoding='utf-8', newline=''), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    for temp_file in outfiles:
        with open(temp_file, 'r', encoding='utf-8') as fid:
            reader = csv.DictReader(fid, delimiter='\t')
            while True:
                try:
                    row  = next(reader)
                    writer.writerow(row)
                except StopIteration:
                    break
                except:
                    print('error in ' + temp_file)

    # remove temp file
    for temp_file in outfiles + split_files:
        os.remove(temp_file)

    print('Done!')