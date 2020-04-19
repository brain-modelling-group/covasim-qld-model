'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
matplotlib.use('TkAgg')
import pandas as pd
import sciris as sc
import covasim as cv
from copy import deepcopy as dcp
from datetime import timedelta
import load_pop
from read_data import i_cases
import numpy as np
import pickle, gzip

# Set state and date
state = 'vic'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-04-19')
n_days    = (end_day - start_day).days

# What to do
todo = ['loaddata',
        'runsim',
        'doplot',
        'showplot',
        'saveplot'
        'diagnose_population'
        ]
verbose    = 1
seed       = 1

date      = '2020apr19'
folder    = f'results_{date}'
file_path = f'{folder}/{state}_'
data_path = f'data/{state}-data-{date}.csv' # This gets created and then read in

# Process and read in data
if 'loaddata' in todo:
    # Read in data
    rawdata = pd.read_json('https://interactive.guim.co.uk/docsdata/1q5gdePANXci8enuiS4oHUJxcxC13d6bjMRSicakychE.json')
    d = pd.json_normalize(rawdata.sheets.updates) # Process data
    d['Date'] = pd.to_datetime(d['Date'], format='%d/%m/%Y')

    # Take state of interest
    sd = dcp(d.loc[(d['State'] == state.upper())])
    sd.rename(columns={'Date': 'date',
                       'Cumulative case count': 'cum_infections',
                       'Cumulative deaths': 'cum_deaths',
                       'Tests conducted (total)': 'cum_test',
                       'Tests conducted (negative)': 'cum_neg',
                       'Hospitalisations (count)': 'n_severe',
                       'Intensive care (count)': 'n_critical',
                       'Recovered (cumulative)': 'cum_recovered'
                       }, inplace=True)
    sd = sd.drop_duplicates(subset=['date'], keep='first')
    sd.set_index('date', inplace=True)
    new_cols = ['cum_infections', 'cum_deaths', 'cum_test', 'cum_neg', 'n_severe', 'n_critical', 'cum_recovered']
    sd = sd[new_cols]
    for c in new_cols:
        sd[c] = pd.to_numeric(sd[c].str.replace(',', ''))

    sd['new_diagnoses'] = sd['cum_infections'].diff()
    sd['new_deaths'] = sd['cum_deaths'].diff()
    sd['new_tests'] = sd['cum_test'].diff()

    for i in pd.date_range(start_day, end_day):
        if i not in sd.index:
            sd.loc[i] = sd.loc[i - timedelta(1)]

    sd.sort_index(inplace=True)
    sd.loc[start_day:end_day].to_csv(data_path)
#sd = pd.read_csv(data_path)

# Set up scenarios
pars = cv.make_pars() # generate some defaults
metapars = cv.make_metapars()
metapars['n_runs'] = 1

pars['pop_size'] = 20000         # This will be scaled
pars['pop_scale'] = 1.0 #6.35e6/pars['pop_size']   # this gives a total VIC population
pars['pop_infected'] = 1        # Number of initial infections
pars['start_day']=start_day     # Start date
pars['n_days']=n_days           # Number of days
pars['use_layers'] = True
pars['contacts'] = {'H': 4, 'S': 22, 'W': 20, 'C': 20, 'Church': 20, 'pSport': 40} # Number of contacts per person per day, estimated
pars['beta_layer'] = {'H': 0.9, 'S': 0.5, 'W': 0.1, 'C': 0.5, 'Church': 0.05, 'pSport': 0.05}
pars['quar_eff'] = {'H': 0.5, 'S': 0.0, 'W': 0.0, 'C': 0.0, 'Church': 0.5, 'pSport': 0.0} # Set quarantine effect for each layer

#popdict = load_pop.get_australian_popdict(setting='Melbourne', pop_size=pars['pop_size'], contact_numbers=pars['contacts'])
#popfile = gzip.open('data\popfile.obj','wb')
#pickle.dump(popdict,popfile)
#popfile.close()
sim = cv.Sim(pars, popfile='data\popfile.obj', datafile=data_path, use_layers=True, pop_size=pars['pop_size'])

#### diagnose population structure
if 'diagnose_population' in todo:
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
    axs[0, 1].bar(range(1,6),h_struct)
    axs[0, 1].set_title("Household size distribution")
    axs[1, 0].hist(s_struct, bins=max(s_struct)-min(s_struct))
    axs[1, 0].set_title("School size distribution")
    axs[1, 1].hist(w_struct, bins=max(w_struct)-min(w_struct))
    axs[1, 1].set_title("Work size distribution")
    axs[2, 0].hist(c_struct, bins=max(c_struct)-min(c_struct))
    axs[2, 0].set_title("Community size distribution")
    matplotlib.pyplot.savefig(fname=file_path + 'population.png')

daily_tests = [0.2*pars['pop_size']]*sim.npts # making up numbers for now

# Cumulative impact of four policy changes on the beta_layers for H, S, W, C, Church, pSports
beta_eff = np.array(((0.5,    1,      1,      0.5,        1,      1), # day 15: international travellers self isolate, public events >500 people cancelled
                     (0.5,    0.5,    0.5,    0.5,      0.0,      1), # day 19: indoor gatherings limited to 100 people
                     (0.5,    0.5,    0.2,    0.1,      0.0,    0.0), # day 22: pubs/bars/cafes take away only, church/sport etc. cancelled
                     (0.5,    0.1,    0.05,   0.05,     0.0,    0.0))) # day 29: public gatherings limited to 2 people

beta_layer_tester = {}
beta_layer_tester = {'H': 0.0, 'S': 0.0, 'W': 0.00, 'C': 0.00, 'Church': 0.00, 'pSport': 0.00} # using this to test while calibrating
scenarios = {#'counterfactual': {'name': 'counterfactual', 'pars': {'interventions': None}}, # no interentions
             'baseline': {'name': 'baseline', 'pars': {'interventions': [cv.dynamic_pars({ #this is what we actually did
#                    'contacts': dict(days=[15, 19, 22, 29],
#                                        vals=[{'H': 4, 'S': 22, 'W': 20, 'C': 20, 'Church': 20, 'pSport': 40},
#                                              {'H': 4, 'S': 0, 'W': 5, 'C': 2, 'Church': 20, 'pSport': 40},
#                                              {'H': 4, 'S': 0, 'W': 5, 'C': 2, 'Church': 20, 'pSport': 40},
#                                              {'H': 4, 'S': 0, 'W': 5, 'C': 2, 'Church': 20, 'pSport': 40}]), # at different time points the contact numbers can change
                    'beta_layer': dict(days=[15, 19, 22, 29], # multiply the beta_layers by the beta_eff
                                        vals=[{'H': beta_eff[0,0]*pars['beta_layer']['H'], 'S': beta_eff[0,1]*pars['beta_layer']['S'], 'W': beta_eff[0,2]*pars['beta_layer']['W'], 'C': beta_eff[0,3]*pars['beta_layer']['C'],'Church': beta_eff[0,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[0,5]*pars['beta_layer']['pSport']},
                                              {'H': beta_eff[1,0]*pars['beta_layer']['H'], 'S': beta_eff[1,1]*pars['beta_layer']['S'], 'W': beta_eff[1,2]*pars['beta_layer']['W'], 'C': beta_eff[1,3]*pars['beta_layer']['C'],'Church': beta_eff[1,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[1,5]*pars['beta_layer']['pSport']},
                                              {'H': beta_eff[2,0]*pars['beta_layer']['H'], 'S': beta_eff[2,1]*pars['beta_layer']['S'], 'W': beta_eff[2,2]*pars['beta_layer']['W'], 'C': beta_eff[2,3]*pars['beta_layer']['C'],'Church': beta_eff[2,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[2,5]*pars['beta_layer']['pSport']},
                                              {'H': beta_eff[3,0]*pars['beta_layer']['H'], 'S': beta_eff[3,1]*pars['beta_layer']['S'], 'W': beta_eff[3,2]*pars['beta_layer']['W'], 'C': beta_eff[3,3]*pars['beta_layer']['C'],'Church': beta_eff[3,4]*pars['beta_layer']['Church'], 'pSport': beta_eff[3,5]*pars['beta_layer']['pSport']},
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=i_cases[0,], vals=i_cases[1,]/pars['pop_scale'])
                        }),
                    cv.test_num(daily_tests=daily_tests, sympt_test=100.0, quar_test=1.0, sensitivity=1.0, test_delay=0, loss_prob=0)]}
                        },
             'baseline2': {'name': 'baseline2', 'pars': {'interventions': [cv.dynamic_pars({ # make a copy to save having to re-run while calibrating
                    'beta_layer': dict(days=[1, 15, 19, 22, 29], # multiply the beta_layers by the beta_eff
                                        vals=[beta_layer_tester,
                                              {'H': beta_eff[0,0]*beta_layer_tester['H'], 'S': beta_eff[0,1]*beta_layer_tester['S'], 'W': beta_eff[0,2]*beta_layer_tester['W'], 'C': beta_eff[0,3]*beta_layer_tester['C'],'Church': beta_eff[0,4]*beta_layer_tester['Church'], 'pSport': beta_eff[0,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff[1,0]*beta_layer_tester['H'], 'S': beta_eff[1,1]*beta_layer_tester['S'], 'W': beta_eff[1,2]*beta_layer_tester['W'], 'C': beta_eff[1,3]*beta_layer_tester['C'],'Church': beta_eff[1,4]*beta_layer_tester['Church'], 'pSport': beta_eff[1,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff[2,0]*beta_layer_tester['H'], 'S': beta_eff[2,1]*beta_layer_tester['S'], 'W': beta_eff[2,2]*beta_layer_tester['W'], 'C': beta_eff[2,3]*beta_layer_tester['C'],'Church': beta_eff[2,4]*beta_layer_tester['Church'], 'pSport': beta_eff[2,5]*beta_layer_tester['pSport']},
                                              {'H': beta_eff[3,0]*beta_layer_tester['H'], 'S': beta_eff[3,1]*beta_layer_tester['S'], 'W': beta_eff[3,2]*beta_layer_tester['W'], 'C': beta_eff[3,3]*beta_layer_tester['C'],'Church': beta_eff[3,4]*beta_layer_tester['Church'], 'pSport': beta_eff[3,5]*beta_layer_tester['pSport']},
                                             ]), # at different time points the FOI can change
                    'n_imports': dict(days=i_cases[0,],
                                      vals=i_cases[1,]/pars['pop_scale'])}),
                    cv.test_num(daily_tests=daily_tests, sympt_test=100.0, quar_test=1.0, sensitivity=1.0, test_delay=0, loss_prob=0)]}
                        }
             }


if __name__ == '__main__': # need this to run in parallel on windows

    if 'runsim' in todo:
        scens = cv.Scenarios(sim=sim, basepars=sim.pars, metapars = metapars, scenarios=scenarios)
        scens.run(verbose=verbose)

    if 'doplot' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        data_plots = ['n_severe', 'n_critical', 'cum_deaths', 'new_deaths', 'new_diagnoses', 'cum_infections']
        for j in data_plots:
            scens.results[j]['data'] = sc.objdict(name='data', best=sd[j][4:].values, low=sd[j][4:].values,
                                                  high=sd[j][4:].values)
        # Configure plotting
        fig_args = dict(figsize=(5, 8))
        this_fig_path = file_path + '.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        to_plot1 = ['new_infections','cum_infections','new_diagnoses','cum_deaths']


        fig1 = scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=8, to_plot=to_plot1)
                            #to_plot = to_plot_health)
                            # = to_plot_capacity)


