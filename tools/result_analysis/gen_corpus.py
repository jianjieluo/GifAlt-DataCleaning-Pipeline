import csv
import os
import argparse

import sys
sys.path.append('tools/result_analysis')
from gramN_match import load_corpus

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=int, default=None,
                        help='the stage of result csv file')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    res_dir = 'result/result_analysis/stage_%d' % args.stage
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    corpus = load_corpus(stage=args.stage, beos=False)
    corpus = sorted(set(corpus))

    res_file = os.path.join(res_dir, 'corpus.txt')
    with open(res_file, 'w') as f:
        for cap in corpus:
            f.write(cap + '\n')
    print("Dump to ", res_file)
