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


    # Process and read in data
    if 'loaddata' in todo:
        sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day, end_day=end_day, data_path=data_path)

    #### diagnose population structure
    if 'gen_pop' in todo:
        popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets = population_subsets)
        sc.saveobj(popfile, popdict)

    pars['beta'] =0.025 # Scale beta
    pars['diag_factor']= 1.6 # Scale proportion asymptomatic
    end_day = sc.readdate('2020-05-07')
    pars['n_days'] = (end_day - start_day).days

    sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
    sim.initialize(save_pop=False, load_pop=True, popfile=popfile)

    # Read a variety of policies from databook sheet 'policies'
    beta_policies, import_policies, clip_policies, policy_dates = load_parameters.load_pols(databook_path=databook_path, layers=pars['contacts'].keys(), start_day=start_day)

    baseline_policies = utils.PolicySchedule(pars['beta_layer'], beta_policies) #create policy schedule with beta layer adjustments
    for d, dates in enumerate(policy_dates): # add start and end dates to beta layer, import and edge clipping policies
        if len(policy_dates[dates]) == 2:
            if dates in beta_policies:
                baseline_policies.add(dates, policy_dates[dates][0], policy_dates[dates][1])
            if dates in import_policies:
                import_policies[dates]['dates'] = np.arange(policy_dates[dates][0], policy_dates[dates][1])
            if dates in clip_policies:
                clip_policies[dates]['dates'] = [policy_dates[dates][0], policy_dates[dates][1]]
        elif len(policy_dates[dates]) == 1:
            if dates in beta_policies:
                baseline_policies.add(dates, policy_dates[dates][0])
            if dates in import_policies:
                import_policies[dates]['dates'] = np.arange(policy_dates[dates][0], n_days)
            if dates in clip_policies:
                clip_policies[dates]['dates'] = [policy_dates[dates][0], n_days]

    base_scenarios = {} #create baseline scenario according to policies from databook
    base_scenarios['baseline'] = {
        'name': 'Baseline',
        'pars': {
            'interventions': [
                baseline_policies,
                cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                    'n_imports': dict(days=range(len(i_cases)), vals=i_cases)
                }),
                cv.test_num(daily_tests=(daily_tests), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
            ]
        }
    }
    # add edge clipping policies to baseline scenario
    for policy in clip_policies:
        details = clip_policies[policy]
        base_scenarios['baseline']['pars']['interventions'].append(cv.clip_edges(start_day=details['dates'][0], end_day=details['dates'][1], change={layer:details['change'] for layer in details['layers']}))

    scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=base_scenarios)
    scens.run(verbose=verbose)

    do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

    # Configure plotting
    fig_args = dict(figsize=(5, 10))
    this_fig_path = file_path + 'baseline.png'
    if for_powerpoint:
        to_plot1 = ['new_infections', 'cum_deaths']
    else:
        to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

    scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=28, fig_args=fig_args,
               font_size=8, to_plot=to_plot1)