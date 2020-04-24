'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
import load_pop
import utils
import numpy as np


# Set state and date
state = 'vic'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-06-19')
n_days    = (end_day - start_day).days

verbose    = 1
seed       = 1

date      = '2020apr19'
folder    = f'results_{date}'
file_path = f'{folder}/{state}_'
data_path = f'data/{state}-data-{date}.csv' # This gets created and then read in
databook_path = f'data/{state}-data.xlsx'
popfile = f'data/popfile.obj'

sd = pd.read_excel(databook_path, sheet_name='epi_data')
sd.rename(columns={'Date': 'date',
                   'Cumulative case count': 'cum_infections',
                   'Cumulative deaths': 'cum_deaths',
                   'Tests conducted (total)': 'cum_test',
                   'Tests conducted (negative)': 'cum_neg',
                   'Hospitalisations (count)': 'n_severe',
                   'Intensive care (count)': 'n_critical',
                   'Recovered (cumulative)': 'cum_recovered',
                   'Daily imported cases': 'daily_imported_cases'
                   }, inplace=True)
sd.set_index('date', inplace=True)
sd.loc[start_day:end_day].to_csv(data_path)

i_cases = np.array(sd['daily_imported_cases'])
i_cases = i_cases[6:len(i_cases)]  # shift 7 days back to account for lag in reporting time
daily_tests = np.array(sd['new_tests'])

# Set up scenarios
pars = cv.make_pars() # generate some defaults
metapars = cv.make_metapars()
metapars['n_runs'] = 3

pars['pop_size'] = 20000         # This will be scaled
pars['pop_scale'] = 1 #6.35e6/pars['pop_size']   # this gives a total VIC population
pars['rescale'] = 0
pars['rescale_threshold'] = 0.8 # Fraction susceptible population that will trigger rescaling if rescaling
pars['rescale_factor'] = 2   # Factor by which we rescale the population
pars['pop_infected'] = 5        # Number of initial infections
pars['start_day']=start_day     # Start date
pars['n_days']=n_days           # Number of days
pars['use_layers'] = True
pars['contacts'] = {'H': 4, 'S': 7, 'W': 5, 'C': 5, 'Church': 1, 'pSport': 1} # Number of contacts per person per day, estimated
pars['beta_layer'] = {'H': 1.0, 'S': 0.5, 'W': 0.5, 'C': 0.1, 'Church': 0.5, 'pSport': 1.0}
pars['quar_eff'] = {'H': 1.0, 'S': 0.0, 'W': 0.0, 'C': 0.0, 'Church': 0.5, 'pSport': 0.0} # Set quarantine effect for each layer
#pars['dynam_layer'] = {'H': 1, 'S': 1, 'W': 1, 'C': 1, 'Church': 1, 'pSport': 1}
pars['beta'] = 0.015

trace_probs = {'H': 1.0, 'S': 0.8, 'W': 0.5, 'C': 0, 'Church': 0.05, 'pSport': 0.1} # contact tracing, probability of finding
trace_time = {'H': 1, 'S': 2, 'W': 2, 'C': 20, 'Church': 10, 'pSport': 5} # number of days to find

print('Making population')
popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'])
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

scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
scens.run(verbose=verbose, debug=True)
to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']
fig_args = dict(figsize=(8, 8))
scens.plot(do_save=False, do_show=True, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)

