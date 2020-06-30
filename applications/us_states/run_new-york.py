import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['New York']
    # the name of the databook
    db_name = 'input_data_US_group2'
    epi_name = 'epi_data_US_group2'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'New York': {'pop_size': int(10e4),
                               'beta': 0.145,
                               'n_days': 370,
                               'symp_test': 100.0,
                               'calibration_end': '2020-06-23'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'New York': {'No changes to current lockdown restrictions': {'replace': (['relax2'], ['relax2'], 
    #                                                     [[140]])}}}
    scen_opts = {'New York': {'Small easing of restrictions on August 1': 
                              {'replace': (['relax2'], [['relax3']], [[164]]),
                              'policies': {'relax3': {'beta': 0.33}}},
                 
                            'Moderate easing of restrictions on August 1': 
                              {'replace': (['relax2'], [['relax4']], [[164]]),
                              'policies': {'relax4': {'beta': 0.43}}},
                 
                            'Small easing of restrictions on July 15': 
                              {'replace': (['relax2'], [['relax3']], [[147]]),
                              'policies': {'relax3': {'beta': 0.33}}},
                 
                            'Moderate easing of restrictions on July 15': 
                              {'replace': (['relax2'], [['relax4']], [[147]]),
                              'policies': {'relax4': {'beta': 0.43}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['relax2'], [['relax2']], [[140]]),
                              'policies': {'relax2': {'beta': 0.5}}}}}
                     
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

    no_release = sum(scens['scenarios']['New York'].results['new_infections']['No changes to current lockdown restrictions']['best'][256:375])
    print('Sum of new infections: No changes to current lockdown restrictions =', no_release)
    august_smallrelease = sum(scens['scenarios']['New York'].results['new_infections']['Small easing of restrictions on August 1']['best'][256:375])
    print('Sum of new infections: Small easing of restrictions on August 1 =', august_smallrelease)
    august_moderaterelease = sum(scens['scenarios']['New York'].results['new_infections']['Moderate easing of restrictions on August 1']['best'][256:375])
    print('Sum of new infections: Moderate easing of restrictions on August 1 =', august_moderaterelease)
    july_smallrelease = sum(scens['scenarios']['New York'].results['new_infections']['Small easing of restrictions on July 15']['best'][256:375])
    print('Sum of new infections: Small easing of restrictions on July 15 =', july_smallrelease)
    july_moderaterelease = sum(scens['scenarios']['New York'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][256:375])
    print('Sum of new infections: Moderate easing of restrictions on on July 15 =', july_moderaterelease)
    

    no_release = scens['scenarios']['New York'].results['cum_infections']['No changes to current lockdown restrictions']['best'][375]
    print('Cumulative infections: No changes to current lockdown restrictions =', no_release)
    august_smallrelease = scens['scenarios']['New York'].results['cum_infections']['Small easing of restrictions on August 1']['best'][375]
    print('Cumulative infections: Small easing of restrictions on August 1 =', august_smallrelease)
    august_moderatelrelease = scens['scenarios']['New York'].results['cum_infections']['Moderate easing of restrictions on August 1']['best'][375]
    print('Cumulative infections: Moderate easing of restrictions on August 1 =', august_moderatelrelease)
    july_smallrelease = scens['scenarios']['New York'].results['cum_infections']['Small easing of restrictions on July 15']['best'][375]
    print('Cumulative infections: Small easing of restrictions on July 15 =', july_smallrelease)
    july_moderatelrelease = scens['scenarios']['New York'].results['cum_infections']['Moderate easing of restrictions on July 15']['best'][375]
    print('Cumulative infections: Moderate easing of restrictions on on July 15 =', july_moderatelrelease)
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                 fig_path=dirname + '/figs/New-York-calibrate' + '.png',
    #                 interval=30, n_cols=1,
    #                 fig_args=dict(figsize=(5, 5), dpi=100),
    #                 font_size=11,
    #                 # y_lim={'new_infections': 500},
    #                 legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                 axis_args={'left': 0.15, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
    #                 fill_args={'alpha': 0.3},
    #                 to_plot=['new_diagnoses', 'cum_deaths'])
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/New-York-projections' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                  axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                  fill_args={'alpha': 0.3},
                  to_plot=['new_infections','cum_infections'])   