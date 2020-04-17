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
import random
import matplotlib.pyplot as plt

# Set state and date
state = 'vic'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-04-14')
n_days    = (end_day - start_day).days

# What to do
todo = ['loaddata',
        'runsim',
        'doplot',
        'showplot',
        'saveplot'
        ]
verbose    = 1
seed       = 1

version   = 'v1'
date      = '2020apr15'
folder    = f'results_{date}'
file_path = f'{folder}/{state}-calibration_{version}'
data_path = f'{state}-data-{date}.csv' # This gets created and then read in

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

    sd.loc[start_day:end_day].to_csv(data_path)

# Set up scenarios
default_pars = cv.make_pars() # generate some defaults
metapars = cv.make_metapars()

#pops_by_age = [1567175,1618776, 1555678, 1502370, 1759111, 1908561, 1891641, 1780923, 1595691, 1678094, 1534763, 1544991, 1388188, 1224849, 1057964, 734277, 505543, 516072]
#prob_dist = [x/sum(pops_by_age) for x in pops_by_age] # convert to probability distribution
#prob_dist = [x/5 for x in prob_dist for _ in range(5)] # spread out to each age rather than 5 age bands
#age_options = [x for x in range(90)] # ages people can be

#draw = random.choices(population = age_options, weights = prob_dist, k=50000)
#plt.hist(draw, bins=90)
#plt.title("Age distribution of model population")

#contacts_list, contact_keys = cv.make_hybrid_contacts(pop_size=50000, ages=draw,
#            contacts = {'h': 4,   's': 22,  'w': 20,  'c': 20}, school_ages = [6, 18], work_ages = [18, 65])

sim = cv.Sim(datafile=data_path, use_layers=True) # this is where population data would be loaded

pars = sc.objdict(
    pop_size=50e3,          # This will be scaled
    pop_infected=5,         # Number of initial infections
    start_day=start_day,    # Start date
    n_days=n_days,          # Number of days
    contacts = {'h': 4,   's': 22,  'w': 20,  'c': 20}, # Number of contacts per person per day, estimated
    beta_layer = {'h': 0.2, 's': 0.8, 'w': 0.1, 'c': 0.3}
)
sim.update_pars(pars) # overwrite  defaults where relevant
scenarios = {'counterfactual': {'name': 'counterfactual', 'pars': {'interventions': None}}, # no interentions
             'baseline': {'name': 'baseline', 'pars': {'interventions': cv.dynamic_pars({ #this is what we actually did
                    'contacts': dict(days=[10, 20],
                                        vals=[{'h': 2, 's': 20, 'w': 15, 'c': 10}, {'h': 2, 's': 0, 'w': 5, 'c': 2}]), # at different time points the contact numbers can change
                    'beta_layer': dict(days=[10, 20],
                                        vals=[{'h': 0.2, 's': 0.8, 'w': 0.1, 'c': 0.3}, {'h': 0.1, 's': 0.0, 'w': 0.0, 'c': 0.3}]), # at different time points the FOI can change
                    'n_imports': dict(days=[0,5], vals=[100,0])})} # at different time points the imported infections can change
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


