import os
import csv
import argparse
import nltk
from multiprocessing import Process
from config import cfg
from models.text_hyper_transformation.hypernymizer import Hypernymizer
from tqdm import tqdm
from lib.utils import stage_item_count

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=str, default='gif_alt_info_clean_7')
    parser.add_argument("--dst", type=str, default='gif_alt_info_clean_8')
    parser.add_argument("--num_worker", type=int, default=4)
    parser.add_argument("--debug", action='store_true')

    args = parser.parse_args()
    assert 0 < args.num_worker
    return args

def filt_too_short(sent):
    sent_len = len(sent.split(' '))
    if sent_len <= cfg.MIN_LEN:
        return 'none'
    else:
        return sent


def hyper_transform(wid, outfile, raw_data):
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']
    writer = csv.DictWriter(open(outfile, 'w', encoding='utf-8'), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    hyper = Hypernymizer()
    with tqdm(total=len(raw_data), ascii=True) as pbar:
        for item in raw_data:
            gid, uid, gifUrl, title, title_pos, alt, alt_pos = item

            if title != 'none' and len(title) > 0:
                title = hyper.transform(title)
                title = filt_too_short(title)
            if alt != 'none' and len(alt) > 0:
                alt = hyper.transform(alt)
                alt = filt_too_short(alt)

            if title != 'none' or alt != 'none':
                title_pos = '\t'.join(title_pos)
                alt_pos = '\t'.join(alt_pos)
                writer.writerow({'gid': gid, 'uid': uid, 'gifUrl': gifUrl, 'title': title,
                'title_pos': title_pos, 'alt': alt, 'alt_pos': alt_pos })
            
            pbar.update(1)


if __name__ == '__main__':
    args = parse_args()
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']

    print("========== Stage 8 Hyper Transform Multi Process ==========")

    # stage_statistician
    total = stage_item_count(args.src)

    # prepare data
    reader = csv.DictReader(open(os.path.join('result', args.src + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
    raw_data = []
    for row in reader:
        gid = row['gid']
        uid = row['uid']
        gifUrl = row['gifUrl']
        title = row['title'].strip()
        title_pos = row['title_pos'].strip().split('\t')
        alt = row['alt'].strip()
        alt_pos = row['alt_pos'].strip().split('\t')
        
        item = (gid, uid, gifUrl, title, title_pos, alt, alt_pos)
        raw_data.append(item)
    
    if args.debug:
        raw_data = raw_data[:4000]
    
    # split and run multi process
    data_splits = [raw_data[i::args.num_worker] for i in range(args.num_worker)]
    procs = []
    outfiles = []
    for w_id, subdata in enumerate(data_splits):
        outfile = os.path.join('result', 'temp' + str(w_id) + '.csv')
        p = Process(target=hyper_transform,
                    args=(w_id, outfile, subdata))
        p.daemon = True
        p.start()
        procs.append(p)
        outfiles.append(outfile)

    for p in procs:
        p.join()

    # grab and merge the internal result
    print("Merge result...")
    writer = csv.DictWriter(open(os.path.join('result', args.dst + '.csv'), 'w', encoding='utf-8'), fieldnames=fieldnames, delimiter='\t')
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
    for temp_file in outfiles:
        os.remove(temp_file)


    print('Done!')