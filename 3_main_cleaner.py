# stage == 1 --> candidates with a high rate of token repetition are discarded
# stage == 2 --> candidates with no determiner, no noun, or no preposition are discarded   
#                candidates with a high noun ratio are also discarded
#                candidates that score too high or too low on the polarity annotations are discarded
# stage == 3 --> remove question
import os
import sys
import csv
import argparse
from models.main_cleaner import MainCleaner
from tqdm import tqdm
from lib.utils import stage_item_count

def parse_args():
    parser = argparse.ArgumentParser(description='alt cleaner')
    parser.add_argument("--dst", type=str, default='gif_alt_info_clean_')
    parser.add_argument("--stage", type=int, default=1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    main_cleaner = MainCleaner()
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']
    main_cleaner.load_model(args.stage)

    reader = csv.DictReader(open(os.path.join('result', args.dst + str(args.stage - 1) + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
    writer = csv.DictWriter(open(os.path.join('result', args.dst + str(args.stage) + '.csv'), 'w', encoding='utf-8', newline=""), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    # stage_statistician
    total = stage_item_count(args.dst + str(args.stage - 1))

    print("========== Stage %d Main Cleaner ==========" % args.stage)
    with tqdm(total=total, ascii=True) as pbar:
        for row in reader:

            gid = row['gid']
            uid = row['uid']
            gifUrl = row['gifUrl']
            title = row['title'].strip()
            title_pos = row['title_pos'].strip().split('\t')
            alt = row['alt'].strip()
            alt_pos = row['alt_pos'].strip().split('\t')

            if title != 'none' and len(title) > 0:
                title = main_cleaner.clean_sent(title, title_pos, args.stage)
            if alt != 'none' and len(alt) > 0:
                alt = main_cleaner.clean_sent(alt, alt_pos, args.stage)

            if title != 'none' or alt != 'none':
                title_pos = '\t'.join(title_pos)
                alt_pos = '\t'.join(alt_pos)
                writer.writerow({'gid': gid, 'uid': uid, 'gifUrl': gifUrl, 'title': title,
                'title_pos': title_pos, 'alt': alt, 'alt_pos': alt_pos })
            
            pbar.update(1)
