'''
Load Australian epi data
'''

import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sciris as sc
import covasim as cv

# Set state and date
state = 'nsw'
start_day = sc.readdate('2020-03-01')
end_day   = sc.readdate('2020-04-14')
n_days    = (end_day - start_day).days

# What to do
todo = ['loaddata',
        'runsim',
        'doplot',
#        'showplot',
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
    sd = d.loc[(d['State'] == state.upper())]
    sd.rename(columns={'Date': 'date',
                       'Cumulative case count': 'cum_pos',
                       'Cumulative deaths': 'cum_death',
                       'Tests conducted (total)': 'cum_test',
                       'Tests conducted (negative)': 'cum_neg',
                       'Hospitalisations (count)': 'n_severe',
                       'Intensive care (count)': 'n_critical',
                       'Recovered (cumulative)': 'cum_recovered'
                       }, inplace=True)
    sd = sd.drop_duplicates(subset=['date'], keep='first')
    sd.set_index('date', inplace=True)
    new_cols = ['cum_pos', 'cum_death', 'cum_test', 'cum_neg', 'n_severe', 'n_critical', 'cum_recovered']
    sd = sd[new_cols]
    for c in new_cols:
        sd[c] = pd.to_numeric(sd[c].str.replace(',', ''))

    sd['new_diagnoses'] = sd['cum_pos'].diff()
    sd['new_deaths'] = sd['cum_death'].diff()
    sd['new_tests'] = sd['cum_test'].diff()

    sd.loc[start_day:end_day].to_csv(data_path)


# Set parameters and run
if 'runsim' in todo:

    # Set the parameters
    default_pars = cv.make_pars()
    sim = cv.Sim(datafile=data_path, use_layers=True)

    pars = sc.objdict(
        pop_size=50e3,          # This will be scaled
        pop_infected=5,         # Number of initial infections
        start_day=start_day,    # Start date
        n_days=n_days,          # Number of days
        beta_layers = {'h': 1.6, 's': 1.0, 'w': 1.0, 'c': 0.3}
    )

    sim.update_pars(pars)
    sim.run(verbose=verbose)

if 'doplot' in todo:

    do_show, do_save = ('showplot' in todo), ('saveplot' in todo)

    # Configure plotting
    to_plot = sc.dcp(cv.default_sim_plots)
    to_plot['Hospital capacity'] = ['n_severe', 'n_critical']
    fig_args = dict(figsize=(20, 24))
    this_fig_path = file_path + '.png'

    fig = sim.plot(do_save=do_save, do_show=do_show, fig_path=this_fig_path, interval=7, fig_args=fig_args, to_plot=to_plot)

