import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__) + '/'

if __name__ == "__main__":
    # the list of locations for this analysis
    locations1 = ['Barcelona10e4']
    locations2 = ['Barcelona5e4']
    # the name of the databook
    db_name = 'input_data_poptest'
    epi_name = 'epi_data_poptest'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars1 = {'Barcelona10e4': {'pop_size': int(10e4),
                               'beta': 0.14,
                               'n_days': 165,
                               'calibration_end': '2020-08-01'}}
    user_pars2 = {'Barcelona5e4': {'pop_size': int(5e4),
                               'beta': 0.14,
                               'n_days': 165,
                               'calibration_end': '2020-08-01'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 4,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    scen_opts1 = {'Barcelona10e4':
                     {'No changes to current lockdown restrictions': 
                             {'replace': (['phase4'], ['phase4'], [[107]])}}}
    scen_opts2 = {'Barcelona5e4':
                     {'No changes to current lockdown restrictions': 
                             {'replace': (['phase4'], ['phase4'], [[107]])}}}
                         
    # set up the scenarios
    scens1 = ui.setup_scens(locations=locations1,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts1,
                           user_pars=user_pars1,
                           metapars=metapars,
                           all_lkeys=all_lkeys,
                           dynamic_lkeys=dynamic_lkeys)
    scens2 = ui.setup_scens(locations=locations2,
                            db_name=db_name,
                            epi_name=epi_name,
                            scen_opts=scen_opts2,
                            user_pars=user_pars2,
                            metapars=metapars,
                            all_lkeys=all_lkeys,
                            dynamic_lkeys=dynamic_lkeys)
    
    # run the scenario
    scens1 = ui.run_scens(scens1)
    scens2 = ui.run_scens(scens2)
    scens1['verbose'] = True
    scens2['verbose'] = True
    
    utils.policy_plot2(scens1, plot_ints=False, do_save=True, do_show=True,
              fig_path=dirname + '/figs' + locations1[0] + '.png',
              interval=30, n_cols = 2,
              fig_args=dict(figsize=(10, 5), dpi=100),
              font_size=11,
              #y_lim={'new_infections': 500},
              legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
              axis_args={'left': 0.1, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
              fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])
    utils.policy_plot2(scens2, plot_ints=False, do_save=True, do_show=True,
                       fig_path=dirname + '/figs' + locations2[0] + '.png',
                       interval=30, n_cols=2,
                       fig_args=dict(figsize=(10, 5), dpi=100),
                       font_size=11,
                       # y_lim={'new_infections': 500},
                       legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
                       axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.99, 'hspace': 0.4, 'bottom': 0.15},
                       fill_args={'alpha': 0.3},
                       to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])