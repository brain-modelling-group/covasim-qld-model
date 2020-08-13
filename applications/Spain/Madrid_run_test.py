import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)
import xlsxwriter
from datetime import date, timedelta
import pandas as pd

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Madrid']
    # the name of the databook
    db_name = 'input_data_Spain'
    epi_name = 'epi_data_Spain'

    # Madridecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Madridecific parameters
    user_pars = {'Madrid': {'pop_size': int(10e4),
                               'beta': 0.14,
                               'n_days': 320,
                               'calibration_end': '2020-08-08'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}

    mid_july = 147 # make this the key date
    end_july = mid_july + 16
    mid_aug = end_july + 15
    end_aug = mid_aug + 15
    mid_sep = mid_aug + 31
    end_sep = mid_sep +15
    mid_oct = mid_sep + 30
    end_oct = mid_sep + 46
    start_nov = end_oct + 1
    mid_nov = end_oct + 15
    end_dec = mid_nov + 46

    # the policies to change during scenario runs
    scen_opts = {'Madrid': {'Ease of restrictions in mid-September': 
                              {'replace': (['restrictions'], [['relax1']], [[mid_sep]])},

                            'Increase of restrictions in mid-September': 
                              {'replace': (['restrictions'], [['relax2']], [[mid_sep]])},

                            'Ease of restrictions in mid-August': 
                              {'replace': (['restrictions'], [['relax1']], [[mid_aug]])},

                            'Increase of restrictions in mid-August': 
                              {'replace': (['restrictions'], [['relax2']], [[mid_aug]])},

                            'No changes to current lockdown restrictions': 
                              {'replace': (['restrictions'], [['restrictions']], [[1]])}}}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)

    # run the scenarios
    scens = ui.run_scens(scens)   
    scens['verbose'] = True

    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Madrid-projection' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 8), dpi=100),
                  font_size=11,
                  # y_lim={'new_infections': 10000},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -3)},
                  axis_args={'left': 0.1, 'wspace': 0.3, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.2},
                  fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses'])