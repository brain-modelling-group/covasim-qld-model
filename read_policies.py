'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop
import numpy as np


if __name__ == '__main__': # need this to run in parallel on windows

    # What to do
    '''Include runsim_indiv and doplot_indiv if you want to produce individual scenario plots against a baseline (assuming 5 importations per day from days 60-90)
    Include runsim_import and doplot_import if you want to produce plots of all scenarios against a baseline (assuming 5, 10, 20, 50 importations per day from days 60-90)'''
    todo = ['loaddata',
            #'runsim_indiv',
            #'doplot_indiv',
            'runsim_import',
            'doplot_import',
            #'showplot',
            'saveplot',
            'gen_pop'
            ]
    for_powerpoint = False
    verbose    = 1
    seed       = 1

    # load parameters
    state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, \
    population_subsets, trace_probs, trace_time = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day, end_day=end_day, data_path=data_path)


    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)
        sc.saveobj(popfile, popdict)

    #sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
    #sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    policies, policy_dates = load_parameters.load_pols(databook_path=databook_path, layers=pars['contacts'].keys(), start_day=start_day)

    baseline_policies = utils.PolicySchedule(pars['beta_layer'], policies)
    for d, dates in enumerate(policy_dates):
        if len(policy_dates[dates]) == 2:
            baseline_policies.add(dates, policy_dates[dates][0], policy_dates[dates][1])
        elif len(policy_dates[dates]) == 1:
            baseline_policies.add(dates, policy_dates[dates][0])
    print('done')