'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes
import numpy as np

if __name__ == '__main__': # need this to run in parallel on windows

    # What to do
    todo = ['loaddata',
            'showplot',
            'saveplot',
            'gen_pop'
            ]
    for_powerpoint = False
    verbose    = 1
    seed       = 1
    restart_imports = 5 # jump start epidemic with imports after day 60

    # load parameters
    state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, \
    population_subsets, trace_probs, trace_time = load_parameters.load_pars()

    if 'loaddata' in todo: # Process and read in data
        sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day, end_day=end_day, data_path=data_path)

    if 'gen_pop' in todo: # generate population and networks
        popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)
        sc.saveobj(popfile, popdict)

    # manually adjust some parameters for calibration, outside of Excel read-in
    pars['beta'] =0.07 # Scale beta
    pars['diag_factor']= 1.6 # Scale proportion asymptomatic for data points in plot of cumulative infections
    end_day = sc.readdate('2020-05-07')
    pars['n_days'] = (end_day - start_day).days

    sim = cv.Sim(pars, popfile=popfile, datafile=data_path, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=databook_path, layers=pars['contacts'].keys(), start_day=start_day)
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, i_cases, daily_tests,n_days,trace_probs, trace_time)

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=base_scenarios)
    scens.run(verbose=verbose)

    # Configure plotting
    do_show, do_save = ('showplot' in todo), ('saveplot' in todo)
    fig_args = dict(figsize=(5, 10))
    this_fig_path = file_path + 'baseline.png'
    if for_powerpoint:
        to_plot1 = ['new_infections', 'cum_deaths']
    else:
        to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

    scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args,
               font_size=8, to_plot=to_plot1)