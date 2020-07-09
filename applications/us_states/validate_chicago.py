import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Chicago']
    # the name of the databook
    db_name = 'input_data_US_group2'
    epi_name = 'epi_data_US_group2'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Chicago': {'pop_size': int(10e4),
                               'beta': 0.139,
                               'n_days': 130,
                               'symp_test': 5.0,
                               'calibration_end': '2020-05-15'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 10,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    scen_opts = {'Chicago': {'No changes to current lockdown restrictions': 
                             {'replace': (['relax1'], ['relax2'], [[107]]),
                              'policies': {'relax2': {'beta': 0.6}}}}}
                         
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
    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
              fig_path=dirname + '/figs/Chicago-validate' + '.png',
              interval=30, n_cols = 2,
              fig_args=dict(figsize=(10, 5), dpi=100),
              font_size=11,
              #y_lim={'new_infections': 500},
              legend_args={'loc': 'upper center', 'bbox_to_anchor': (1.0, -1.6)},
              axis_args={'left': 0.08, 'wspace': 0.2,'right': 0.99, 'hspace': 0.4,'bottom': 0.15},
              fill_args={'alpha': 0.3},
              to_plot=['new_infections', 'cum_infections', 'cum_diagnoses', 'cum_deaths'])