import csv
import argparse
import os
import sys
sys.path.append('tools/result_analysis')
from pre_release_statistics import pre_release_statistics

parser = argparse.ArgumentParser()
parser.add_argument('--stages', type=str, default='0,1,2,3,4,5')
parser.add_argument('--check_url', action="store_true")
args = parser.parse_args()

stages = [int(x) for x in args.stages.split(',')]

for stage in stages:
    csv_path = 'result/gif_alt_info_clean_%d.csv' % stage

    if os.path.exists(csv_path):
        print('######## Stage %d ########' % stage)
        pre_release_statistics(stage, args.check_url)