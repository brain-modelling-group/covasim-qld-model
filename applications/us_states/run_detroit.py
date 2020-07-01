import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Detroit']
    # the name of the databook
    db_name = 'input_data_US_group2'
    epi_name = 'epi_data_US_group2'

    # specify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-specific parameters
    user_pars = {'Detroit': {'pop_size': int(10e4),
                               'beta': 0.135,
                               'n_days': 370,
                               'calibration_end': '2020-06-30'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'Detroit': {'No changes to current lockdown restrictions': {'replace': (['relax3'], ['relax3'], 
    #                                                     [[140]])}}}
    scen_opts = {'Detroit': {'Small easing of restrictions on August 15': 
                              {'replace': (['relax3'], [['relax4']], [[173]]),
                              'policies': {'relax4': {'beta': 0.6}}},
                 
                            'Moderate easing of restrictions on August 15': 
                              {'replace': (['relax3'], [['relax5']], [[173]]),
                              'policies': {'relax5': {'beta': 0.7}}},
                 
                            'Small easing of restrictions on July 15': 
                              {'replace': (['relax3'], [['relax4']], [[142]]),
                              'policies': {'relax4': {'beta': 0.6}}},
                 
                            'Moderate easing of restrictions on July 15': 
                              {'replace': (['relax3'], [['relax5']], [[142]]),
                              'policies': {'relax5': {'beta': 0.7}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['relax3'], [['relax3']], [[140]]),
                              'policies': {'relax3': {'beta': 0.5}}}}}
                     
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

    new_no_release = sum(scens['scenarios']['Detroit'].results['new_infections']['No changes to current lockdown restrictions']['best'][251:370])    
    new_august_smallrelease = sum(scens['scenarios']['Detroit'].results['new_infections']['Small easing of restrictions on August 15']['best'][251:370])    
    new_august_moderaterelease = sum(scens['scenarios']['Detroit'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][251:370])    
    new_july_smallrelease = sum(scens['scenarios']['Detroit'].results['new_infections']['Small easing of restrictions on July 15']['best'][251:370])
    new_july_moderaterelease = sum(scens['scenarios']['Detroit'].results['new_infections']['Moderate easing of restrictions on July 15']['best'][251:370])
    cum_no_release = scens['scenarios']['Detroit'].results['cum_infections']['No changes to current lockdown restrictions']['best'][370]
    cum_august_smallrelease = scens['scenarios']['Detroit'].results['cum_infections']['Small easing of restrictions on August 15']['best'][370]
    cum_august_moderatelrelease = scens['scenarios']['Detroit'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][370]
    cum_july_smallrelease = scens['scenarios']['Detroit'].results['cum_infections']['Small easing of restrictions on July 15']['best'][370]
    cum_july_moderatelrelease = scens['scenarios']['Detroit'].results['cum_infections']['Moderate easing of restrictions on July 15']['best'][370]
    
    with open('Detroit_projections.txt', 'w') as f:
        print('Sum of new infections: No changes to current lockdown restrictions =', new_no_release, file=f)
        print('Sum of new infections: Small easing of restrictions on August 15 =', new_august_smallrelease, file=f)
        print('Sum of new infections: Moderate easing of restrictions on August 15 =', new_august_moderaterelease, file=f)
        print('Sum of new infections: Small easing of restrictions on July 15 =', new_july_smallrelease, file=f)
        print('Sum of new infections: Moderate easing of restrictions on on July 15 =', new_july_moderaterelease, file=f)
        print('Cumulative infections: No changes to current lockdown restrictions =', cum_no_release, file=f)
        print('Cumulative infections: Small easing of restrictions on August 15 =', cum_august_smallrelease, file=f)
        print('Cumulative infections: Moderate easing of restrictions on August 15 =', cum_august_moderatelrelease, file=f)
        print('Cumulative infections: Small easing of restrictions on July 15 =', cum_july_smallrelease, file=f)
        print('Cumulative infections: Moderate easing of restrictions on on July 15 =', cum_july_moderatelrelease, file=f)
        f.close()
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                 fig_path=dirname + '/figs/Detroit-calibrate' + '.png',
    #                 interval=30, n_cols=1,
    #                 fig_args=dict(figsize=(5, 5), dpi=100),
    #                 font_size=11,
    #                 # y_lim={'new_infections': 500},
    #                 legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
    #                 axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.15},
    #                 fill_args={'alpha': 0.3},
    #                 to_plot=['new_diagnoses', 'cum_deaths'])
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Detroit-projections' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                  axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                  fill_args={'alpha': 0.3},
                  to_plot=['new_infections','cum_infections'])   