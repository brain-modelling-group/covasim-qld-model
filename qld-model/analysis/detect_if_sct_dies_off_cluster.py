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

folder_list_cluster = ['/home/paula/Dropbox/COVID/simulated-data/resurgence/case-cloz',
                       '/home/paula/Dropbox/COVID/simulated-data/resurgence/case-cluk',
                       '/home/paula/Dropbox/COVID/simulated-data/resurgence/case-clin']





# List of files to plot
list_of_files = ['qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0001.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0002.obj', 
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0003.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0004.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0005.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0006.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0007.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0008.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0009.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0010.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0011.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0012.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0013.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0014.obj',
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0015.obj']

 
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
 