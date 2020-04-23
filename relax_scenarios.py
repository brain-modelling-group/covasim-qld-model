'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
#matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
from copy import deepcopy as dcp
import load_pop
import numpy as np
import pickle, gzip

# Set state and date
state = 'vic'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-06-19')
n_days    = (end_day - start_day).days

# What to do
'''Include runsim_indiv and doplot_indiv if you want to produce individual scenario plots against a baseline (assuming 5 importations per day from days 60-90)
Include runsim_import and doplot_import if you want to produce plots of all scenarios against a baseline (assuming 5, 10, 20, 50 importations per day from days 60-90)'''
todo = ['loaddata',
        #'runsim_indiv',
        #'doplot_indiv',
        'runsim_import',
        'doplot_import',
        'showplot',
        'saveplot',
       'gen_pop'
        ]

if not 'doplot_indiv' in todo:
    matplotlib.use('TkAgg')

verbose    = 1
seed       = 1

date      = '2020apr19'
folder    = f'results_{date}'
file_path = f'{folder}/{state}_'
data_path = f'data/{state}-data-{date}.csv' # This gets created and then read in
databook_path = f'data/{state}-data.xlsx'
popfile = f'data/popfile.obj'

# Process and read in data
if 'loaddata' in todo:
    sd = pd.read_excel(databook_path, sheet_name = 'epi_data')
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


#### diagnose population structure
if 'gen_pop' in todo:
    popdict = load_pop.get_australian_popdict(databook_path, pop_size=pars['pop_size'], contact_numbers=pars['contacts'])
    popfile_save = gzip.open(popfile,'wb')
    pickle.dump(popdict,popfile_save)
    popfile_save.close()
    s_struct, w_struct, c_struct = [],[],[]
    h_struct = np.zeros(6)
    for i in range(0,pars['pop_size']-1):
        s_struct.append(len(popdict['contacts'][i]['S']) + 1)
        w_struct.append(len(popdict['contacts'][i]['W']) + 1)
        c_struct.append(len(popdict['contacts'][i]['C']) + 1)
        h_struct[len(popdict['contacts'][i]['H'])] += 1
    h_struct / np.array((1, 2, 3, 4, 5, 6)) # account for over counting of households
    fig_pop, axs = matplotlib.pyplot.subplots(3, 2)
    axs[0, 0].hist(popdict['age'], bins=max(popdict['age'])-min(popdict['age']))
    axs[0, 0].set_title("Age distribution of model population")
    axs[0, 1].bar(np.array((1,2,3,4,5,6)),h_struct)
    axs[0, 1].set_title("Household size distribution")
    axs[1, 0].hist(s_struct, bins=max(s_struct)-min(s_struct))
    axs[1, 0].set_title("School size distribution")
    axs[1, 1].hist(w_struct, bins=max(w_struct)-min(w_struct))
    axs[1, 1].set_title("Work size distribution")
    axs[2, 0].hist(c_struct, bins=max(c_struct)-min(c_struct))
    axs[2, 0].set_title("Community size distribution")
    #matplotlib.pyplot.savefig(fname=file_path + 'population.png')

sim = cv.Sim(pars, popfile=popfile, datafile=data_path, use_layers=True, pop_size=pars['pop_size'])
beta_days = [1, 15, 19, 22, 29, 60]
# Cumulative impact of four policy changes on the beta_layers for H, S, W, C, Church, pSports
beta_eff2 = np.array(((1.02,    1,      1,      0.98,        1,      1), # day 15: international travellers self isolate, public events >500 people cancelled
                     (1.05,    0.75,    1,    0.9,      0.0,      1), # day 19: indoor gatherings limited to 100 people
                     (1.06,    0.5,    0.88,    0.82,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                     (1.13,    0.25,    0.67,   0.55,     0.0,    0.0), # day 29: public gatherings limited to 2 people
                     (1,1,1,1,1,1))) # go back to pre-lockdown

beta_eff_relax = np.array(((0.0,    0.0,      0.0,      0.14,        0.0,      0.0), # day 60: relax outdoor gatherings to 10 people
                     (0.0,    0.0,    0.05,    0.27,      0.0,      0.0), # day 60: non-essential retail outlets reopen
                     (0.0,    0.0,    0.04,    0.16,      0.0,    0.0), # day 60: restaurants/cafes/bars allowed to do eat in with 4 sq m distancing
                     (0.0,    0.0,    0.0,    0.04,      0.0,      0.0), # day 60: relax outdoor gatherings to 200 people
                     (0.0,    0.0,    0.0,    0.08,      0.0,      0.0), # day 60: community sports reopen
                     (0.0,    0.75,    0.0,   0.0,     0.0,    0.0), # day 60: childcare and schools reopen
                     (0.0,    0.0,    0.33,   0.0,     0.0,    0.0), # day 60: non-essential work reopens
                     (0.0,    0.0,    0.0,   0.0,     0.0,    1), # day 60: professional sport without crowds allowed
                     (0.0,    0.0,    0.0,   0.0,     1,    0.0))) # day 60: places of worship reopen
beta_eff_relax[:,:-2] = 1 + beta_eff_relax[:,:-2]/beta_eff2[3,:-2] # rescale changes to be proportional to beta_layer at the end of the lockdown

beta_layer_tester = pars['beta_layer'] #{'H': 1.7, 'S': 0.8, 'W': 0.5, 'C': 0.1, 'Church': 0.5, 'pSport': 1.0} #{'H': 0.0, 'S': 0.0, 'W': 0.00, 'C': 0.05, 'Church': 0.00, 'pSport': 0.00} # using this to test while calibrating
beta_layer_interventions = {'H': beta_eff2[3,0]*pars['beta_layer']['H'], 'S': beta_eff2[3,1]*pars['beta_layer']['S'], 'W': beta_eff2[3,2]*pars['beta_layer']['W'], 'C': beta_eff2[3,3]*pars['beta_layer']['C'],'Church': beta_eff2[3,4]*pars['beta_layer']['Church'], 'pSport': beta_eff2[3,5]*pars['beta_layer']['pSport']}
base_scenarios = {'baseline2': {'name': 'baseline2', 'pars': {'interventions': [cv.dynamic_pars({ # what we actually did but re-introduce imported infections to test robustness
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days[:-1], # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[5]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        }}
scen_names = ['Outdoor10', 'Retail', 'Hospitalitylimited', 'Outdoor200', 'Sports', 'School', 'Work', 'ProSports', 'Church']
relax_scenarios = {'Int0': {'name': 'Fullrelax', 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline 2 but with all restrictions lifted
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days, # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[4,0]*beta_layer_tester['H'], 'S': beta_eff2[4,1]*beta_layer_tester['S'], 'W': beta_eff2[4,2]*beta_layer_tester['W'], 'C': beta_eff2[4,3]*beta_layer_tester['C'],'Church': beta_eff2[4,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[4,5]*beta_layer_tester['pSport']}
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[5]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        }}
for n, name in enumerate(scen_names):
    relax_scenarios['Int'+str(n+1)] = {'name': name, 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline 2 but with all restrictions lifted
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days, # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff_relax[n,0]*beta_layer_interventions['H'], 'S': beta_eff_relax[n,1]*beta_layer_interventions['S'], 'W': beta_eff_relax[n,2]*beta_layer_interventions['W'], 'C': beta_eff_relax[n,3]*beta_layer_interventions['C'],'Church': beta_eff_relax[n,4], 'pSport': beta_eff_relax[n,5]}
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[5]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        }
relax_scenarios['Int10'] = {'name': 'Borders', 'pars': {'interventions': [cv.dynamic_pars({ # Same as baseline2 but increase importations for border reopening
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days[:-1], # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[10]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        }



if __name__ == '__main__': # need this to run in parallel on windows

    for run in relax_scenarios.keys():
        if 'runsim_indiv' in todo:
            scenarios = base_scenarios
            scenarios[run] = relax_scenarios[run]
            scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
            scens.run(verbose=verbose)
            del base_scenarios[run]

        if 'doplot_indiv' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(5, 8))
            this_fig_path = file_path + relax_scenarios[run]['name'] + '.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            to_plot1 = ['new_infections','cum_infections','new_diagnoses','cum_deaths']


            scens.plot(do_save=do_save, do_show=False, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)

    for imports in [5, 10, 20, 50]:
        import_scenarios = {'baseline2': {'name': 'baseline2', 'pars': {'interventions': [cv.dynamic_pars({ # what we actually did but re-introduce imported infections to test robustness
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days[:-1], # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[imports]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [10000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        },
                    'Int0': {'name': 'Fullrelax', 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline 2 but with all restrictions lifted
                    'beta': dict(days=[1], vals=pars['beta']),
                    'beta_layer': dict(days=beta_days, # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff2[4,0]*beta_layer_tester['H'], 'S': beta_eff2[4,1]*beta_layer_tester['S'], 'W': beta_eff2[4,2]*beta_layer_tester['W'], 'C': beta_eff2[4,3]*beta_layer_tester['C'],'Church': beta_eff2[4,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[4,5]*beta_layer_tester['pSport']}
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                      vals=np.append(i_cases,[imports]*30))}),
                    cv.test_num(daily_tests=np.append(daily_tests, [10000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                    cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                        }}
        for n, name in enumerate(scen_names):
            import_scenarios['Int'+str(n+1)] = {'name': name, 'pars': {'interventions': [cv.dynamic_pars({ # same as baseline 2 but with all restrictions lifted
                            'beta': dict(days=[1], vals=pars['beta']),
                            'beta_layer': dict(days=beta_days, # multiply the beta_layers by the beta_eff
                                                vals=[beta_layer_tester,
                                                      {'H': beta_eff2[0,0]*beta_layer_tester['H'], 'S': beta_eff2[0,1]*beta_layer_tester['S'], 'W': beta_eff2[0,2]*beta_layer_tester['W'], 'C': beta_eff2[0,3]*beta_layer_tester['C'],'Church': beta_eff2[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[0,5]*beta_layer_tester['pSport']},
                                                      {'H': beta_eff2[1,0]*beta_layer_tester['H'], 'S': beta_eff2[1,1]*beta_layer_tester['S'], 'W': beta_eff2[1,2]*beta_layer_tester['W'], 'C': beta_eff2[1,3]*beta_layer_tester['C'],'Church': beta_eff2[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[1,5]*beta_layer_tester['pSport']},
                                                      {'H': beta_eff2[2,0]*beta_layer_tester['H'], 'S': beta_eff2[2,1]*beta_layer_tester['S'], 'W': beta_eff2[2,2]*beta_layer_tester['W'], 'C': beta_eff2[2,3]*beta_layer_tester['C'],'Church': beta_eff2[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[2,5]*beta_layer_tester['pSport']},
                                                      {'H': beta_eff2[3,0]*beta_layer_tester['H'], 'S': beta_eff2[3,1]*beta_layer_tester['S'], 'W': beta_eff2[3,2]*beta_layer_tester['W'], 'C': beta_eff2[3,3]*beta_layer_tester['C'],'Church': beta_eff2[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff2[3,5]*beta_layer_tester['pSport']},
                                                      {'H': beta_eff_relax[n,0]*beta_layer_interventions['H'], 'S': beta_eff_relax[n,1]*beta_layer_interventions['S'], 'W': beta_eff_relax[n,2]*beta_layer_interventions['W'], 'C': beta_eff_relax[n,3]*beta_layer_interventions['C'],'Church': beta_eff_relax[n,4], 'pSport': beta_eff_relax[n,5]}
                                                     ]), # at different time points the FOI can change
                            'n_imports': dict(days=np.append(range(len(i_cases)), np.arange(60, 90)),
                                              vals=np.append(i_cases,[imports]*30))}),
                            cv.test_num(daily_tests=np.append(daily_tests, [1000]*50), sympt_test=100.0, quar_test=1.0, sensitivity=0.7, test_delay=3, loss_prob=0),
                            cv.contact_tracing(trace_probs=trace_probs, trace_time=trace_time, start_day=0)]}
                                }

        if 'runsim_import' in todo:
            scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars=metapars, scenarios=import_scenarios)
            scens.run(verbose=verbose)

        if 'doplot_import' in todo:
            do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

            # Configure plotting
            fig_args = dict(figsize=(8, 8))
            this_fig_path = file_path + str(imports) + 'imports.png'
            to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
            to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
            to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
            to_plot_capacity = ['n_severe', 'n_critical']
            to_plot1 = ['new_infections', 'cum_infections', 'new_diagnoses', 'cum_deaths']

            scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1, as_dates=False)


