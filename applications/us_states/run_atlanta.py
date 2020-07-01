import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Atlanta']
    # the name of the databook
    db_name = 'input_data_US_group2'
    epi_name = 'epi_data_US_group2'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Atlanta': {'pop_size': int(10e4),
                               'beta': 0.065,
                               'n_days': 365,
                               'symp_test': 100.0,
                               'calibration_end': '2020-06-27'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.03,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'Atlanta': {'No changes to current lockdown restrictions': {'replace': (['relax3'], ['relax3'], 
    #                                                     [[140]])}}}
    scen_opts = {'Atlanta': {'Small easing of restrictions on August 15': 
                              {'replace': (['relax2'], [['relax3']], [[167]]),
                              'policies': {'relax3': {'beta': 0.65}}},
                 
                            'Moderate easing of restrictions on August 15': 
                              {'replace': (['relax2'], [['relax4']], [[167]]),
                              'policies': {'relax4': {'beta': 0.8}}},
                 
                            'Small easing of restrictions on July 15': 
                              {'replace': (['relax2'], [['relax3']], [[136]]),
                              'policies': {'relax3': {'beta': 0.65}}},
                 
                            'Moderate easing of restrictions on July 15': 
                              {'replace': (['relax2'], [['relax4']], [[136]]),
                              'policies': {'relax4': {'beta': 0.8}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['relax2'], [['relax2']], [[120]]),
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
    

    no_release = sum(scens['scenarios']['Atlanta'].results['new_infections']['No changes to current lockdown restrictions']['best'][245:364])
    print('Sum of new infections: No changes to current lockdown restrictions =', no_release)
    august_smallrelease = sum(scens['scenarios']['Atlanta'].results['new_infections']['Small easing of restrictions on August 15']['best'][245:364])
    print('Sum of new infections: Small easing of restrictions on August 15 =', august_smallrelease)
    august_moderaterelease = sum(scens['scenarios']['Atlanta'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][245:364])
    print('Sum of new infections: Moderate easing of restrictions on August 15 =', august_moderaterelease)
    july_smallrelease = sum(scens['scenarios']['Atlanta'].results['new_infections']['Small easing of restrictions on July 15']['best'][245:364])
    print('Sum of new infections: Small easing of restrictions on July 15 =', july_smallrelease)
    july_moderaterelease = sum(scens['scenarios']['Atlanta'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][245:364])
    print('Sum of new infections: Moderate easing of restrictions on on July 15 =', july_moderaterelease)
    

    no_release = scens['scenarios']['Atlanta'].results['cum_infections']['No changes to current lockdown restrictions']['best'][364]
    print('Cumulative infections: No changes to current lockdown restrictions =', no_release)
    august_smallrelease = scens['scenarios']['Atlanta'].results['cum_infections']['Small easing of restrictions on August 15']['best'][364]
    print('Cumulative infections: Small easing of restrictions on August 15 =', august_smallrelease)
    august_moderatelrelease = scens['scenarios']['Atlanta'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][364]
    print('Cumulative infections: Moderate easing of restrictions on August 15 =', august_moderatelrelease)
    july_smallrelease = scens['scenarios']['Atlanta'].results['cum_infections']['Small easing of restrictions on July 15']['best'][364]
    print('Cumulative infections: Small easing of restrictions on July 15 =', july_smallrelease)
    july_moderatelrelease = scens['scenarios']['Atlanta'].results['cum_infections']['Moderate easing of restrictions on July 15']['best'][364]
    print('Cumulative infections: Moderate easing of restrictions on on July 15 =', july_moderatelrelease)
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                fig_path=dirname + '/figs/Atlanta-calibrate' + '.png',
    #                interval=30, n_cols=1,
    #                fig_args=dict(figsize=(5, 5), dpi=100),
    #                font_size=11,
    #                # y_lim={'new_infections': 500},
    #                legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
    #                fill_args={'alpha': 0.3},
    #                to_plot=['new_diagnoses', 'cum_deaths'])
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Atlanta-projections' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                  axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                  fill_args={'alpha': 0.3},
                  to_plot=['new_infections','cum_infections'])   