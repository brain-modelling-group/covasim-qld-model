#!/usr/bin/env python
# coding: utf-8
"""
Load obj files and caluclate additinoal stats 

python collate_resurgence_results.py 
--filelist_path '/home/paula/mnt_avalon/mnt/lustre/working/lab_jamesr/paulaSL/covid-results/pbs.14809560/sim-data' \
--filelist_name 'filelist_obj.csv' 

for n in *.csv; do printf '%s\n' "$n"; done > filelist.txt

# author Paula Sanz-Leon, QIMRB 2021

"""

import pandas as pd
import argparse
import sciris as sc

from pathlib import Path

parser = argparse.ArgumentParser()



parser.add_argument('--filelist_obj_name', 
                        type=str, 
                        help='''The name of the file with csv file names where results are stored''')

parser.add_argument('--filelist_path', 
                        type=str, 
                        help='''The absolute path to a file with csv file names where results are stored''')

parser.add_argument('--result_name', 
                        type=str, 
                        help='''The relative and/or absolute path to a results csv file''')
args = parser.parse_args()





with open(f"{args.filelist_path}/{args.filelist_name}", 'r') as f:
        content = f.readlines()
        filelist = [l.strip() for l in content] 

        for f_idx, fname in enumerate(filelist):
            fname_csv = fname.with_suffix('.csv')
            msim = sc.loadobj(f"{args.filelist_path}/{fname}")

            median_trace, data = utils.get_ensemble_trace('new_infections', msim.sims, **{'convolve': True, 'num_days': 3})
            
            # Get ensemble first case 
            idx_date = utils.detect_first_case(median_trace)

            utils.get_num_infections('new_infections', msims.sims, **{'convolve': True, 'num_days': 3})


    