#!/usr/bin/env python
# coding: utf-8
"""
Load obj files and caluclate additinoal stats 

python calculate_resurgence_stats.py 
--filelist_path '/home/paula/mnt_avalon/mnt/lustre/working/lab_jamesr/paulaSL/covid-results/pbs.14809560/sim-data' \
--filelist_obj_name 'filelist_obj.csv' 

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
import numpy as np
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
            median_trace_inf, data_inf = utils.get_ensemble_trace('new_infections', msim.sims, **{'convolve': False, 'num_days': 1})

            # Get ensemble outbreak
            idx_date = utils.detect_outbreak(median_trace_inf[1:])
            ou_day_av, ou_day_md, ou_day_sd, ou_prob, uc_prob, co_prob  = utils.calculate_outbreak_stats(data_inf[1:, ...])

            if idx_date is not None:
              outbreak_data = {'resurgence': True}
              idx_date +=1
            else:
              outbreak_data = {'resurgence': False}

            df_ou_inf_dict  = sc.mergedicts(outbreak_data, 
                                            {'resurgence_day': [idx_date], 
                                             'resurgence_day_av': [ou_day_av],
                                             'resurgence_day_md': [ou_day_md],
                                             'resurgence_day_sd': [ou_day_sd],
                                             'resurgence_prob': [ou_prob],
                                             'resurgence_control_prob': [uc_prob],
                                             'resurgence_contained_prob': [co_prob]}
                                                     )

            fc_idx_date = utils.detect_first_case(median_trace)
            if fc_idx_date is None:
                fc_num_infections = np.nan
            else:
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
            
            # Replace values
            for key in df_dict.keys(): 
                df_ou[key] = df_dict[key]
            for key in df_ou_inf_dict:
                df_ou[key] = df_ou_inf_dict[key] 

            #df_ou_inf = pd.DataFrame.from_dict(df_ou_inf_dict)

            #df = pd.concat([df_ou, df_ou_inf], axis=1)

            # save 
            df_ou.to_csv(f"{args.filelist_path}/{fname_csv}")

    
