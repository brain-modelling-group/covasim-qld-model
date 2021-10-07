#!/usr/bin/env python
# coding: utf-8
"""
Detect cases that cross the SCT threshold but then die off

"""

import sciris as sc
import numpy as np
import covasim as cv
from covasim_australia import utils

# Filepaths

folder_list_cluster = ['/home/paula/Dropbox/COVID/simulated-data/resurgence/case-ploz',
                       '/home/paula/Dropbox/COVID/simulated-data/resurgence/case-pluk',
                       '/home/paula/Dropbox/COVID/simulated-data/resurgence/case-plin']





# List of files to plot
list_of_files = ['qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.1000.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.1500.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.2000.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.2500.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.3000.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.3500.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.4000.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.4500.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.5000.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.5500.obj',
                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.6000.obj']

 
case_labels = ['A22', 'B117', 'B167']                     

for idx, results_folder in enumerate(folder_list_cluster):
    num_cases = len(list_of_files)
    for file_idx, this_file in enumerate(list_of_files):
        msim = sc.loadobj(f'{results_folder}/{this_file}')
        sims = msim.sims
        data = utils.get_individual_traces('new_infections', sims, convolve=False, num_days=1)
        dies_off_prob, dies_off_prob_1000, day_off_list, day_off_av, day_off_md, day_off_sd  = utils.calculate_sct_supression(data)    
        print(case_labels[idx])
        print(list_of_files[file_idx])
        print(dies_off_prob)
        print(dies_off_prob_1000)
        print(day_off_list)        
 