import os
import csv
import argparse
from tqdm import tqdm
import sys
sys.path.append('tools/result_analysis')
from pre_release_statistics import pre_release_statistics

class GramN(object):
    def __init__(self, args):
        super(GramN, self).__init__()
        self.gram1_freq = {}
        self.gram2_freq = {}
        self.gram3_freq = {}
        self.gram4_freq = {}
        self.gram5_freq = {}

        self.beos = bool(args.beos == 1)
        self.beos_only = bool(args.beos_only == 1)
        if self.beos_only:
            assert self.beos == True
        if self.beos:
            self.gram6_freq = {}

    def add_gram(self, sent):
        sent = '<bos> %s <eos>' % sent if self.beos else sent

        words = sent.split(' ')
        for w in words:
            self.gram1_freq[w] = self.gram1_freq.get(w, 0) + 1
        for i in range(len(words) - 1):
            w = (words[i], words[i+1])
            self.gram2_freq[w] = self.gram2_freq.get(w, 0) + 1
        for i in range(len(words) - 2):
            w = (words[i], words[i+1], words[i+2])
            self.gram3_freq[w] = self.gram3_freq.get(w, 0) + 1
        for i in range(len(words) - 3):
            w = (words[i], words[i+1], words[i+2], words[i+3])
            self.gram4_freq[w] = self.gram4_freq.get(w, 0) + 1
        for i in range(len(words) - 4):
            w = (words[i], words[i+1], words[i+2], words[i+3], words[i+4])
            self.gram5_freq[w] = self.gram5_freq.get(w, 0) + 1
        if self.beos:
            for i in range(len(words) - 5):
                w = (words[i], words[i+1], words[i+2], words[i+3], words[i+4], words[i+5])
                self.gram6_freq[w] = self.gram6_freq.get(w, 0) + 1

    def output(self, res_dir):
        self.output_gram(self.gram1_freq, os.path.join(res_dir, 'gram1_freq.txt'))
        self.output_gram(self.gram2_freq, os.path.join(res_dir, 'gram2_freq.txt'))
        self.output_gram(self.gram3_freq, os.path.join(res_dir, 'gram3_freq.txt'))
        self.output_gram(self.gram4_freq, os.path.join(res_dir, 'gram4_freq.txt'))
        self.output_gram(self.gram5_freq, os.path.join(res_dir, 'gram5_freq.txt'))
        if self.beos:
            self.output_gram(self.gram6_freq, os.path.join(res_dir, 'gram6_freq.txt'))

    def output_gram(self, gram_freq, path):
        cw = sorted([(count,w) for w,count in gram_freq.items()], reverse=True)
        with open(path, 'w') as fid:
            for ent in cw:
                if ent[0] > 20:
                    gram = ent[1] if type(ent[1]) is str else ' '.join(ent[1])
                    if self.beos_only:
                        if '<bos>' in gram or '<eos>' in gram:
                            fid.write(gram + '\t' + str(ent[0]) + '\n')
                    else:
                        fid.write(gram + '\t' + str(ent[0]) + '\n')

def parse_args():
    parser = argparse.ArgumentParser(description='gram analysis')
    parser.add_argument('--stage', type=int, default=None)
    parser.add_argument('--beos', type=int, default=1)
    parser.add_argument('--beos_only', type=int, default=1)
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--check_url', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    gram = GramN(args)

    print("Begin generating GramN...")
    if args.release:
        valid_captions, _ = pre_release_statistics(args.stage, check_url=args.check_url)
        with tqdm(total=len(valid_captions), ascii=True) as pbar:
            for cap in valid_captions:
                gram.add_gram(cap)
                pbar.update(1)
    else:
        src = 'result/gif_alt_info_clean_%d.csv' % args.stage
        reader = csv.DictReader(open(src, 'r'), delimiter='\t')
        count = 0
        for row in reader:
            count += 1
            if count % 20000 == 0:
                print(count)

            uid = row['uid']
            gifUrl = row['gifUrl']
            title = row['title'].strip().lower()
            title_pos = row['title_pos'].strip().split('\t')
            alt = row['alt'].strip().lower()
            alt_pos = row['alt_pos'].strip().split('\t')

            if title != 'none' and len(title) > 0:
                gram.add_gram(title)
            if alt != 'none' and len(alt) > 0:
                gram.add_gram(alt)

    res_dir = 'result/result_analysis/stage_%d/GramN' % args.stage
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    gram.output(res_dir)
