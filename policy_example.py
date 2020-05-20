'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import load_pop, load_parameters
import utils
import numpy as np

todo = ['loaddata',
        # 'runsim_indiv',
        # 'doplot_indiv',
        'runsim_import',
        'doplot_import',
        # 'showplot',
        'saveplot',
        'gen_pop'
        ]
verbose    = 1
seed       = 1

state, start_day, end_day, n_days, date, folder, file_path, data_path, databook_path, popfile, pars, metapars, \
population_subsets, trace_probs, trace_time = load_parameters.load_pars()

# Process and read in data
if 'loaddata' in todo:
    sd, i_cases, daily_tests = load_parameters.load_data(databook_path=databook_path, start_day=start_day,
                                                         end_day=end_day, data_path=data_path)

print('Making population')
popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'], population_subsets=population_subsets)
print('Made population')
sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
print('Making policies')

policies = {}
policies['day15'] = dict(H=1.02, C=0.98)  # day 15: international travellers self isolate , public events >500 people cancelled
policies['day19'] = dict(H=1.05, S=0.75, C=0.9, Church=0.0)  # day 19: indoor gatherings limited to 100 people
policies['day22'] = dict(H=1.06, S=0.5, W=0.88, C=0.82, Church=0.0, pSport=0.0)  # day 22: pubs/bars/cafes take away only                                     , church/sport etc. cancelled
policies['day29'] = dict(H=1.13, S=0.25, W=0.67, C=0.55, Church=0.0, pSport=0.0)  # day 29: public gatherings limited to 2 people

# CAUTION - make sure these values are relative to baseline, not relative to day 29
policies['Outdoor10'] = dict(C=1.04, Church=0.0, pSport=0.0)  # day 60: relax outdoor gatherings to 10 people
policies['Retail'] = dict( W=1.05, C=1.27, Church=0.0, pSport=0.0)  # day 60: non-essential retail outlets reopen
policies['Hospitalitylimited'] = dict(W=1.04, C=1.16, Church=0.0, pSport=0.0)  # day 60: restaurants/cafes/bars allowed to do eat in with 4 sq m distancing
policies['Outdoor200'] = dict(C=1.04, Church=0.0, pSport=0.0)  # day 60: relax outdoor gatherings to 200 people
policies['Sports'] = dict(C=1.08, Church=0.0, pSport=0.0)  # day 60: community sports reopen
policies['School'] = dict(S=1.75, Church=0.0, pSport=0.0)  # day 60: childcare and schools reopen
policies['Work'] = dict(W=1.33, Church=0.0, pSport=0.0)  # day 60: non-essential work reopens
policies['ProSports'] = dict(Church=0.0)  # day 60: professional sport without crowds allowed
policies['Church'] = dict(pSport=0.0)  # day 60: places of worship reopen

baseline_policies = utils.PolicySchedule(pars['beta_layer'],policies)
baseline_policies.add('day15',15,19)
baseline_policies.add('day19',19,22)
baseline_policies.add('day22',22,29)
baseline_policies.add('day29',29) # Add this policy without an end day


scenarios = {}
scenarios['counterfactual'] = {
    'name': 'counterfactual',
    'pars': {
        'interventions': [
            cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [5] * 30))
            }),
            cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
            cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
        ]
    }
}

scenarios['baseline'] = {
    'name': 'baseline',
    'pars': {
        'interventions': [
            baseline_policies,
            cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [5] * 30))
            }),
            cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
            cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
        ]
    }
}


relax_all_policies = sc.dcp(baseline_policies)
relax_all_policies.end('day29',60)
scenarios['Fullrelax'] = {
    'name': 'Fullrelax',
    'pars': {
        'interventions': [
            relax_all_policies,
            cv.dynamic_pars({  # what we actually did but re-introduce imported infections to test robustness
                'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),vals=np.append(i_cases, [5] * 30))
            }),
            cv.test_num(daily_tests=np.append(daily_tests, [1000] * 50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
            cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)
        ]
    }
}

baseline_policies.plot_gantt()
relax_all_policies.plot_gantt()

scens = cv.Scenarios(sim=sim, basepars=pars, metapars = metapars, scenarios=scenarios)
scens.run(verbose=verbose, debug=True)
to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']
fig_args = dict(figsize=(8, 8))
scens.plot(do_save=False, do_show=True, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)

