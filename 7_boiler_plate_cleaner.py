# predefined boiler-plate prefix/suffix
import os
import csv
import argparse
from models.boiler_plate_cleaner import BoilerPlateCleaner
from tqdm import tqdm
from lib.utils import stage_item_count

def parse_args():
    parser = argparse.ArgumentParser(description='alt cleaner')
    parser.add_argument("--src", type=str, default='gif_alt_info_clean_6')
    parser.add_argument("--dst", type=str, default='gif_alt_info_clean_7')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    fieldnames = ['gid', 'uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']
    cleaner2 = BoilerPlateCleaner('txt/boiler_plate2.txt')
    cleaner3 = BoilerPlateCleaner('txt/boiler_plate3.txt')

    reader = csv.DictReader(open(os.path.join('result', args.src + '.csv'), 'r', encoding='utf-8'), delimiter='\t')
    writer = csv.DictWriter(open(os.path.join('result', args.dst + '.csv'), 'w', encoding='utf-8', newline=""), fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    # stage_statistician
    total = stage_item_count(args.src)

    print("========== Stage 7 Boiler_Plate Cleaner ==========")
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
                title = cleaner2.clean_sent(title)
            if title != 'none' and len(title) > 0:
                title = cleaner3.clean_sent(title)
            if alt != 'none' and len(alt) > 0:
                alt = cleaner2.clean_sent(alt)
            if alt != 'none' and len(alt) > 0:
                alt = cleaner3.clean_sent(alt)

            if title != 'none' or alt != 'none':
                title_pos = '\t'.join(title_pos)
                alt_pos = '\t'.join(alt_pos)
                writer.writerow({'gid': gid, 'uid': uid, 'gifUrl': gifUrl, 'title': title,
                'title_pos': title_pos, 'alt': alt, 'alt_pos': alt_pos })
            
            pbar.update(1)

