import os
import sys
import csv
import argparse
import string

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=int, default=None,
                        help='the stage of result csv file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    res_dir = 'result/result_analysis/stage_%d' % args.stage
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    tags = set()
    with open('txt/tags_refine.txt', 'r') as fid:
        for line in fid:
            tags.add(line.strip())

    fieldnames = ['uid', 'gifUrl', 'title', 'title_pos',  'alt', 'alt_pos']
    csv_file = 'result/gif_alt_info_clean_%d.csv' % args.stage
    reader = csv.DictReader(open(csv_file, 'r'), delimiter='\t')

    count = 0
    sents_freq = {}
    word_freq = {}
    for row in reader:
        count += 1
        if count % 20000 == 0:
            print(count)

        uid = row['uid']
        gifUrl = row['gifUrl']
        title = row['title'].strip()
        title_pos = row['title_pos'].strip().split('\t')
        alt = row['alt'].strip()
        alt_pos = row['alt_pos'].strip().split('\t')

        sents_freq[title] = sents_freq.get(title, 0) + 1
        sents_freq[alt] = sents_freq.get(alt, 0) + 1

        words = alt.split()
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        words = title.split()
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1


    cw = sorted([(count,w) for w,count in sents_freq.items()], reverse=True)
    path = os.path.join(res_dir, 'sent_freq.txt')
    with open(path, 'w') as fid:
        for ent in cw:
            fid.write(ent[1] + '\t' + str(ent[0]) + '\n')
    print("Dump to ", path)

    cw = sorted([(count,w) for w,count in word_freq.items()], reverse=True)
    path = os.path.join(res_dir, 'word_freq.txt')
    with open(path, 'w') as fid:
        for ent in cw:
            if ent[1] in tags:
               fid.write(ent[1] + '\t' + str(ent[0]) + '\n')
    print("Dump to ", path)