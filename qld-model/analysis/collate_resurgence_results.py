#!/usr/bin/env python
# coding: utf-8
"""
Load csv files and collate them into one file

# author Paula Sanz-Leon, QIMRB 2021

"""

import pandas as pd
import argparse



parser = argparse.ArgumentParser()


parser.add_argument('--filename', 
                        type=str, 
                        help='''The relative and/or absolute path to a file with csv file names where results are stored''')

parser.add_argument('--resultname', 
                        type=str, 
                        help='''The relative and/or absolute path to a results csv file''')
args = parser.parse_args()


def load_file(fname):
    frame = pd.read_csv(fname)
    return frame


with open(args.filename, 'r') as f:
        content = f.readlines()
        filelist = [l.strip() for l in content] 
        frames = [load_file(fname) for fname in filelist]
        result = pd.concat(frames)
        result.to_csv(args.resultname)