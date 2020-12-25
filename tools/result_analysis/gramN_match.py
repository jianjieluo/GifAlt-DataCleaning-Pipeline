from tqdm import tqdm
import argparse
import os
import csv
import random
random.seed(1)

MAX_MATCH = 50


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=int, default=None,
                        help='the stage of result csv file')
    parser.add_argument('--ngram', type=int, default=6,
                        help='your target gram n')
    parser.add_argument('--beos', type=int, default=1,
                        help='whether to consider <bos> and <eos>')

    args = parser.parse_args()
    return args


def read_ngram(n, stage):
    ngram_path = 'result/result_analysis/stage_%d/GramN/gram%d_freq.txt' % (
        stage, n)
    print('Read ngram file ', ngram_path, '...')
    with open(ngram_path, 'r') as fid:
        ngram = [
            (
                ' '.join(line.strip().split('\t')[:-1]),
                int(line.strip().split('\t')[-1])
            ) for line in fid
        ]
    return ngram


def load_corpus(stage, beos):
    corpus_path = 'result/gif_alt_info_clean_%d.csv' % stage
    print('Load corpus from ', corpus_path, '...')
    corpus = []
    reader = csv.DictReader(open(corpus_path, 'r'), delimiter='\t')
    for row in reader:
        title = row['title'].strip().lower()
        alt = row['alt'].strip().lower()

        if title != 'none':
            sent = '<bos> %s <eos>' % title if beos else title
            corpus.append(sent)
        if alt != 'none':
            sent = '<bos> %s <eos>' % alt if beos else alt
            corpus.append(sent)

    origin_count = len(corpus)
    corpus = list(set(corpus))
    unique_count = len(corpus)
    print('Origin captions count: %d\nUnique captions count: %d' %
          (origin_count, unique_count))
    print('Unique ratio: ', unique_count / origin_count)
    return corpus


def main(args):
    res_dir = 'result/result_analysis/stage_%d/GramN_matched/' % args.stage
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    ngram = read_ngram(args.ngram, args.stage)
    corpus = load_corpus(args.stage, args.beos == 1)

    ngram = sorted(ngram, key=lambda x: x[1], reverse=True)
    ngram = [x[0] for x in ngram]

    progress = tqdm(range(len(ngram)), ascii=True)
    with open(os.path.join(res_dir, 'gram%d_matched.txt' % args.ngram), 'w') as fid:
        for i in progress:
            gram = ngram[i]
            matched = [x for x in corpus if gram in x]
            if len(matched) >= 2 * MAX_MATCH:
                random.shuffle(matched)
            matched = matched[:MAX_MATCH]

            fid.write('\n%d:\t' % i + gram + '\n')
            for cap in matched:
                fid.write(cap + '\n')
    print("Done!")


if __name__ == '__main__':
    args = parse_args()
    main(args)
