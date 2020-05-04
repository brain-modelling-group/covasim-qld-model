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
            #'gen_pop'
            ]
    for_powerpoint = False
    verbose    = 1
    seed       = 1

    # load parameters
    pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(databook_path=extra_pars['databook_path'],
                                                                                         start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'])

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)

    # manually adjust some parameters for calibration, outside of Excel read-in
    pars['beta'] = 0.125 # Scale beta
    pars['diag_factor'] = 1.6 # Scale proportion asymptomatic
    pars['n_days'] = 70

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars)

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=base_scenarios)
    scens.run(verbose=verbose)

    # Configure plotting
    do_show, do_save = ('showplot' in todo), ('saveplot' in todo)
    fig_args = dict(figsize=(5, 10))
    this_fig_path = extra_pars['file_path'] + 'baseline.png'
    if for_powerpoint:
        to_plot1 = scens.results['new_infections']
    else:
        to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

    utils.policy_plot(scens, plot_ints=False, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args,
               font_size=8, to_plot=to_plot1)