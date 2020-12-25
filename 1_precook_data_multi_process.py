import os
import sys
import csv
import argparse
from models.basic_cleaner import TokenizedBasicCleaner
from multiprocessing import Process
from tqdm import tqdm
from lib.utils import stage_item_count
from tokenization_bert import BertTokenizer

def parse_args():
    parser = argparse.ArgumentParser(description='precook data')
    parser.add_argument('--src', type=str, default=None)
    parser.add_argument("--dst", type=str, default='gif_alt_info_clean')
    parser.add_argument("--num_worker", type=int, default=4)
    parser.add_argument("--remove_punc", action="store_true")

    args = parser.parse_args()
    assert 0 < args.num_worker
    return args

args = parse_args()

def sub_process(wid, infile, outfile, total):
    fieldnames = ['uid','gifUrl', 'title', 'alt']
    reader = csv.DictReader(open(infile, 'r', encoding='utf-8'), delimiter='\t')
    writer = csv.DictWriter(open(outfile, 'w', encoding='utf-8', newline=''), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    cleaner = TokenizedBasicCleaner(args, tokenizer)
    with tqdm(total=total, ascii=True) as pbar:
        for row in reader:
            pbar.update(1)
            
            uid = row['uid']
            gifUrl = row['gifUrl']
            title = row['title'].strip().lower()
            alt = row['alt'].strip().lower()

            gifUrl_lower = gifUrl.lower()
            if cleaner.check_url(gifUrl_lower) == False:
                continue
            gifUrl = cleaner.complete_url(gifUrl)

            if title != 'none' and len(title) > 0:
                title = cleaner.clean_sent(title)
            if alt != 'none' and len(alt) > 0:
                alt = cleaner.clean_sent(alt)

            if title != 'none' or alt != 'none':
                writer.writerow({ 'uid': uid, 'gifUrl': gifUrl, 'title': title, 'alt': alt })
    

if __name__ == '__main__':
    fieldnames = ['uid','gifUrl', 'title', 'alt']

    print("========== Stage 1 Precook Data ==========")

    # split data
    reader = csv.DictReader(open(os.path.join('result', args.src + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
    split_files = [os.path.join('result', 'split' + str(wid) + '.csv') for wid in range(args.num_worker)]

    fids = [open(file, 'w', encoding='utf-8', newline='') for file in split_files]
    writers = [csv.DictWriter(fid, fieldnames=fieldnames, delimiter='\t') for fid in fids]
    for w in writers:
        w.writeheader()

    totals = {}
    for i, row in enumerate(reader):
        uid = row['uid']
        gifUrl = row['gifUrl']
        title = row['title'].strip().lower()
        alt = row['alt'].strip().lower()

        wid = i % args.num_worker
        writers[wid].writerow({ 'uid': uid, 'gifUrl': gifUrl, 'title': title, 'alt': alt })
        totals[wid] = totals.get(wid, 0) + 1

    for f in fids:
        f.close()

    # split and run multi process
    procs = []
    outfiles = []
    for w_id, infile in enumerate(split_files):
        outfile = os.path.join('result', 'temp' + str(w_id) + '.csv')
        p = Process(target=sub_process,
                    args=(w_id, infile, outfile, totals[w_id]))
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
