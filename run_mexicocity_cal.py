import user_interface as ui
import utils
import os

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Mexico city']
    # the name of the databook
    db_name = 'input_data_mexico'
    epi_name = 'epi_data_mexico'

    # country-specific parameters
    user_pars = {'Mexico city': {'pop_size': int(10e4),
                               'beta': 0.15,
                               'n_days': 368}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Mexico city': {'phase1': {'beta': 0.8},
                              'phase2': {'beta': 0.1}, 
                              'phase3': {'beta': 0.25}}}

    # Note that lockdown 3 comes into effect the first time at day 90
    
    # the policies to change during scenario runs
    policy_change = {'Mexico city': {'lockdown restrictions relaxed by 15% on August 30': {'replace': (['phase2'], [['phase3']],
                                                        [[186]])},
                                     'lockdown restrictions relaxed by 15% on July 30': {'replace': (['phase2'], [['phase3']],
                                                        [[155]])}}}
                     
    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    # run the scenarios
    # scens = ui.run_scens(scens)  
    # scens['verbose'] = True
    # dirname = os.path.dirname(__file__)
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #               fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/Mexico' + '/Mexico city-calibration' + '.png',
    #               interval=30,
    #               fig_args=dict(figsize=(10, 5), dpi=100),
    #               font_size=11,
    #               #y_lim={'new_infections': 500},
    #               legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
    #               axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
    #               fill_args={'alpha': 0.0},
    #               to_plot=['cum_deaths'])
    scens = ui.run_scens(scens)
    scens['verbose'] = True
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path='C:/Users/farah/Documents/covasim-australia-feature-international/figures/Mexico' + '/Mexico-city' + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
                  fill_args={'alpha': 0.0},
                  to_plot=['new_infections'])
   

    August_release = sum(scens['Mexico city'].results['new_infections']['lockdown restrictions relaxed by 15% on August 30']['best'][249:368])
    print('Restrictions relaxed in August =', August_release)
    September_release = sum(scens['Mexico city'].results['new_infections']['lockdown restrictions relaxed by 15% on July 30']['best'][249:368])
    print('Restrictions relaxed in September  =', September_release)