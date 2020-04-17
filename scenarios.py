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
import matplotlib.pyplot as plt
import load_pop
from read_data import i_cases

# Set state and date
state = 'vic'
start_day = sc.readdate('2020-01-25')
end_day   = sc.readdate('2020-04-14')
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

date      = '2020apr15'
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

# Set up scenarios
pars = cv.make_pars() # generate some defaults
metapars = cv.make_metapars()

pars['pop_size'] = 5000         # This will be scaled
pars['pop_scale'] = 10e3        # this gives a total population of 5M
pars['pop_infected'] = 5        # Number of initial infections
pars['start_day']=start_day     # Start date
pars['n_days']=n_days           # Number of days
pars['contacts'] = {'H': 4, 'S': 22, 'W': 20, 'C': 20} # Number of contacts per person per day, estimated
pars['beta_layer'] = {'H': 0.2, 'S': 0.8, 'W': 0.1, 'C': 0.3}
pars['quar_eff'] = {'H': 0.5, 'S': 0.0, 'W': 0.0, 'C': 0.0} # Set quarantine effect for each layer

popdict = load_pop.get_australian_popdict(setting='Melbourne', pop_size=pars['pop_size'], contact_numbers=pars['contacts'])
sim = cv.Sim(pars, datafile=data_path)

#### diagnose population structure
if 'diagnose_population' in todo:
    h_struct, s_struct, w_struct, c_struct = [],[],[],[]
    for i in range(0,pars['pop_size']-1):
        h_struct.append(len(popdict['contacts'][i]['H']) + 1)
        s_struct.append(len(popdict['contacts'][i]['S']) + 1)
        w_struct.append(len(popdict['contacts'][i]['W']) + 1)
        c_struct.append(len(popdict['contacts'][i]['C']) + 1)
    fig_pop, axs = plt.subplots(3, 2)
    axs[0, 0].hist(popdict['age'], bins=max(popdict['age'])-min(popdict['age']))
    axs[0, 0].set_title("Age distribution of model population")
    axs[0, 1].hist(h_struct, bins=max(h_struct)-min(h_struct))
    axs[0, 1].set_title("Household size distribution")
    axs[1, 0].hist(s_struct, bins=max(s_struct)-min(s_struct))
    axs[1, 0].set_title("School size distribution")
    axs[1, 1].hist(w_struct, bins=max(w_struct)-min(w_struct))
    axs[1, 1].set_title("Work size distribution")
    axs[2, 0].hist(c_struct, bins=max(c_struct)-min(c_struct))
    axs[2, 0].set_title("Community size distribution")
    plt.savefig(fname=file_path + 'population.png')

daily_tests = [0.002*pars['pop_size']]*sim.npts # making up numbers for now

scenarios = {'counterfactual': {'name': 'counterfactual', 'pars': {'interventions': None}}, # no interentions
             'baseline': {'name': 'baseline', 'pars': {'interventions': [cv.dynamic_pars({ #this is what we actually did
                    'contacts': dict(days=[10, 20],
                                        vals=[{'H': 2, 'S': 20, 'W': 15, 'C': 10}, {'H': 2, 'S': 0, 'W': 5, 'C': 2}]), # at different time points the contact numbers can change
                    'beta_layer': dict(days=[10, 20],
                                        vals=[{'H': 0.2, 'S': 0.8, 'W': 0.1, 'C': 0.3}, {'H': 0.1, 'S': 0.0, 'W': 0.0, 'C': 0.3}]), # at different time points the FOI can change
                    'n_imports': dict(days=i_cases[0,],
                                      vals=i_cases[1,])}),
                    cv.test_num(daily_tests=daily_tests),
                    cv.test_prob(symp_prob=0.001, asymp_prob=0.0)]} # not sure how this part works yet
                        }
             }


if __name__ == '__main__': # need this to run in parallel on windows

    if 'runsim' in todo:
        scens = cv.Scenarios(basepars=sim.pars, metapars = metapars, scenarios=scenarios)
        scens.run(verbose=verbose)

    if 'doplot' in todo:
        do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

        data_plots = ['n_severe', 'n_critical', 'cum_deaths', 'new_deaths', 'new_diagnoses', 'cum_infections']
        for j in data_plots:
            scens.results[j]['data'] = sc.objdict(name='data', best=sd[j][3:].values, low=sd[j][3:].values,
                                                  high=sd[j][3:].values)
        # Configure plotting
        fig_args = dict(figsize=(5, 8))
        this_fig_path = file_path + '.png'
        to_plot_cum = ['cum_infections', 'cum_diagnoses', 'cum_recoveries']
        to_plot_daily = ['new_infections', 'new_diagnoses', 'new_recoveries', 'new_deaths']
        to_plot_health = ['cum_severe', 'cum_critical', 'cum_deaths']
        to_plot_capacity = ['n_severe', 'n_critical']
        to_plot1 = ['new_infections','cum_infections','new_diagnoses','cum_deaths']


        fig1 = scens.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, font_size=10, to_plot=to_plot1)
                            #to_plot = to_plot_health)
                            # = to_plot_capacity)


