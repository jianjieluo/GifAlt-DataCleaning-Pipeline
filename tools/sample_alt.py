import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--src', type=str, default=None)
parser.add_argument('--dst', type=str, default=None)
parser.add_argument('--frac', type=float, default=0.1)
args = parser.parse_args()
assert 0 < args.frac <= 1

print("Load data file %s" % args.src)
df = pd.read_csv(args.src, delimiter='\t', encoding='utf-8', low_memory=False)

df_sample = df.sample(frac=args.frac)
df_sample.to_csv(args.dst, sep='\t', encoding='utf-8')

df_debug = df_sample.head(100)
df_debug.to_csv('result/debug_gif_alt_info.csv', sep='\t', encoding='utf-8')