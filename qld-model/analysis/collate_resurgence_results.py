#!/usr/bin/env python
# coding: utf-8
"""
Load csv files and collate them into one file

python collate_resurgence_results.py 
--filelist_path '/home/paula/mnt_avalon/mnt/lustre/working/lab_jamesr/paulaSL/covid-results/pbs.14809560/sim-data' \
--filelist_name 'filelist.txt' 
--result_name 'outbreak_14809560.txt'


# author Paula Sanz-Leon, QIMRB 2021

"""

import pandas as pd
import argparse



parser = argparse.ArgumentParser()



parser.add_argument('--filelist_name', 
                        type=str, 
                        help='''The name of  ile with csv file names where results are stored''')

parser.add_argument('--filelist_path', 
                        type=str, 
                        help='''The absolute path to a file with csv file names where results are stored''')

parser.add_argument('--result_name', 
                        type=str, 
                        help='''The relative and/or absolute path to a results csv file''')
args = parser.parse_args()


def load_file(fname):
    frame = pd.read_csv(fname)
    return frame


with open(f"{args.filelist_path}/{args.filelist_name}", 'r') as f:
        content = f.readlines()
        filelist = [l.strip() for l in content] 
        frames = [load_file(f"{args.filelist_path}/{fname}") for fname in filelist]
        result = pd.concat(frames)
        result.to_csv(f"{args.filelist_path}/{args.result_name}")