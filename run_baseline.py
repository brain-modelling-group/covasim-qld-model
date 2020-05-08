'''
Load Australian epi data
'''

import matplotlib
import pandas as pd
import sciris as sc
import covasim as cv
import utils, load_parameters, load_pop, policy_changes, os
import load_parameters_int, load_pop_int
import numpy as np
dirname = os.path.dirname(os.path.abspath(__file__))

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

    # load parameters
    pars, metapars, extra_pars, population_subsets = load_parameters.load_pars()

    # Process and read in data
    if 'loaddata' in todo:
        sd, extra_pars['i_cases'], extra_pars['daily_tests'] = load_parameters.load_data(databook_path=extra_pars['databook_path'],
                                                                                         start_day=pars['start_day'], end_day=extra_pars['end_day'], data_path=extra_pars['data_path'], setting=extra_pars['setting'])

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(extra_pars['databook_path'], pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets, setting=extra_pars['setting'])
        sc.saveobj(extra_pars['popfile'], popdict)

    # manually adjust some parameters for calibration, outside of Excel read-in
    pars['beta'] = 0.1 # Scale beta
    pars['diag_factor'] = 1.6 # Scale proportion asymptomatic
    pars['n_days'] = 60

    sim = cv.Sim(pars, popfile=extra_pars['popfile'], datafile=extra_pars['data_path'], pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=extra_pars['popfile'])

    # Read a variety of policies from databook sheet 'policies', and set up the baseline according to their start and end dates
    policies = policy_changes.load_pols(databook_path=extra_pars['databook_path'], layers=pars['contacts'].keys(),
                                        start_day=pars['start_day'])
    # Set up a baseline scenario that includes all policy changes to date
    base_scenarios, baseline_policies = policy_changes.set_baseline(policies, pars, extra_pars, popdict)

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=base_scenarios)
    scens.run(verbose=verbose)

    # Configure plotting
    do_show, do_save = ('showplot' in todo), ('saveplot' in todo)
    fig_args = dict(figsize=(5, 10))
    this_fig_path = dirname + '/figures/baseline.png'
    if for_powerpoint:
        to_plot1 = scens.results['new_infections']
    else:
        to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

    utils.policy_plot(scens, plot_ints=True, do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=14, fig_args=fig_args,
               font_size=8, to_plot=to_plot1)

    labels = utils.pretty_label
    fig =baseline_policies.plot_gantt(max_time=pars['n_days'], start_date=pars['start_day'],
                                                     pretty_labels=labels)
    fig.savefig(fname=dirname + '/figures/base_policies.png')
    # fig.show()