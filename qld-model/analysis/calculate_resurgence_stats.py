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
#!/usr/bin/env python
# coding: utf-8
"""
python calculate_resurgence_stats.py \
--filelist_path '/home/paula/mnt_avalon/mnt/lustre/working/lab_jamesr/paulaSL/covid-results/pbs.14821845/sim-data' \
--filelist_obj_name 'filelist_obj_test.csv'
"""

import pandas as pd
import argparse
import sciris as sc
import covasim_australia.utils as utils

from pathlib import Path

parser = argparse.ArgumentParser()



parser.add_argument('--filelist_obj_name', 
                        type=str, 
                        help='''The name of the file with csv file names where results are stored''')

parser.add_argument('--filelist_path', 
                        type=str, 
                        help='''The absolute path to a file with csv file names where results are stored''')

args = parser.parse_args()





with open(f"{args.filelist_path}/{args.filelist_obj_name}", 'r') as f:
        content = f.readlines()
        filelist = [l.strip() for l in content] 

        for f_idx, fname in enumerate(filelist):
            fname_obj = Path(fname)
            fname_csv = fname_obj.with_suffix('.csv')
            msim = sc.loadobj(f"{args.filelist_path}/{fname}")

            # Save basic results to csv
            df_ou = pd.read_csv(f"{args.filelist_path}/{fname_csv}")

            # Get ensemble and convolve
            median_trace, data = utils.get_ensemble_trace('new_diagnoses', msim.sims, **{'convolve': True, 'num_days': 3})
            median_trace_inf, data_inf = utils.get_ensemble_trace('new_infections', msim.sims, **{'convolve': True, 'num_days': 3})

            fc_idx_date = utils.detect_first_case(median_trace)
            fc_num_infections = median_trace_inf[fc_idx_date]
            fc_day_av, fc_day_md, fc_day_sd, fc_inf_av, fc_inf_md, fc_inf_sd = utils.calculate_first_case_stats(data, data_inf)
            df_dict  = {'first_case_day': [fc_idx_date], 
                        'first_case_day_av': [fc_day_av],
                        'first_case_day_md': [fc_day_md],
                        'first_case_day_sd': [fc_day_sd],
                        'first_case_inf': [fc_num_infections],
                        'first_case_inf_av': [fc_inf_av],
                        'first_case_inf_md': [fc_inf_md],
                        'first_case_inf_sd': [fc_inf_sd]}
           
            df_fc = pd.DataFrame.from_dict(df_dict)

            df = pd.concat([df_ou, df_fc], axis=1)

            # merge dataframes

            # save 
            df.to_csv(f"{args.filelist_path}/{fname_csv}")

    