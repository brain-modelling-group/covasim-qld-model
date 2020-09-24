import user_interface as ui
import utils
import os
from datetime import date, timedelta
import pandas as pd
import pickle

dirname = os.path.dirname(__file__)
import xlsxwriter

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Boise']
    # the name of the databook
    db_name = 'input_data_US_group1'
    epi_name = 'epi_data_US_group1'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Boise': {'pop_size': int(10e4),
                        'beta': 0.052,
                        'n_days': 155,
                        'pop_infected': 60,
                        'calibration_end': '2020-08-15'}}

    mid_july = 130 # make this the key date
    mid_aug = mid_july + 31
    mid_sep = mid_aug + 31
    end_oct = mid_sep + 46
    mid_nov = end_oct + 15
    end_dec = mid_nov + 46

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    # the policies to change during scenario runs

    scen_opts = {'Boise': { 'No changes to current lockdown restrictions':
                                {'replace': (['policy_1'], [['policy_3']], [[370]])}
                                  }}


    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    # run the scenario
    scens = ui.run_scens(scens)
    scens['verbose'] = True

    utils.policy_plot2(scens, plot_ints=False, do_save=False, do_show=True,
                       fig_path=dirname + '/figs/Boise-calibrate' + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])

