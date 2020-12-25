import argparse
import os
import sys
sys.path.append('tools/result_analysis')
from gramN_match import load_corpus

parser = argparse.ArgumentParser()
parser.add_argument('--before', type=int, default=None)
parser.add_argument('--after', type=int, default=None)
args = parser.parse_args()

res_dir = 'tools/result_analysis/compare_results'
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

res_path = os.path.join(res_dir, 'filted_sents_between_%d_and_%d.txt' % (args.before, args.after))
before_corpus = load_corpus(args.before, beos=False)
after_corpus = load_corpus(args.after, beos=False)

res = set(before_corpus) - set(after_corpus)
print('New remove nums: ', len(res))
res = sorted(res)

print('Dump to ', res_path)
with open(res_path, 'w') as f:
    for r in res:
        f.write(r + '\n')