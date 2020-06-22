import user_interface as ui
import utils

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Chicago']
    # the name of the databook
    db_name = 'input_data_US'
    epi_name = 'epi_data_US'

    # country-specific parameters
    user_pars = {'Chicago': {'pop_size': int(10e4),
                               'beta': 0.076,
                               'pop_infected': 5,
                               'n_days': 150}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}
    
    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Chicago': {'lockdown1': {'beta': 0.8},
                              'lockdown2': {'beta': 0.5}, 
                              'lockdown3': {'beta': 0.218},
                              'lockdown4': {'beta': 0.3},
                              'relax1': {'beta': 0.3}, 
                              'relax2': {'beta': 0.35},
                              'relax3': {'beta': 0.4}}}
    
    # the policies to change during scenario runs
    policy_change = {'Chicago': {'lockdown restrictions relaxed by 5% on September 30': {'replace': (['relax2'], [['relax3']], 
                                                        [[219]])}}}
    # policy_change = {'Chicago': {'lockdown relaxed by 10% on September 1': {'replace': (['lockdown4'], [['relax3']], 
    #                                                     [[190]])},
    #                              'lockdown relaxed by 20% on October 1': {'replace': (['lockdown4'], [['lockdown2']], 
    #                                                      [[220]])}}}
                     
    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    # run the scenarios
    scens = ui.run_scens(scens)   
    scens['verbose'] = True
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #               fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/Chicago-calibration' + '.png',
    #               interval=30,
    #               fig_args=dict(figsize=(10, 5), dpi=100),
    #               font_size=11,
    #               #y_lim={'new_infections': 500},
    #               legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
    #               axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
    #               fill_args={'alpha': 0.0},
    #               to_plot=['cum_deaths'])
    
    # plot cumulative deaths for calibration
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                  fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/Chicago-new_diag' + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
                  fill_args={'alpha': 0.0},
                  to_plot=['new_diagnoses'])
    
    # plot new infections, data of interest
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #                     fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/Chicago-new_inf' + '.png',
    #               interval=30,
    #               fig_args=dict(figsize=(10, 5), dpi=100),
    #               font_size=11,
    #               #y_lim={'new_infections': 500},
    #               legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
    #               axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
    #               fill_args={'alpha': 0.0},
    #               to_plot=['new_infections'])
    
    # # plot cumulative infections to see if all the population gets infected    
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #               fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/Chicago-cum_inf' + '.png',
    #               interval=30,
    #               fig_args=dict(figsize=(10, 5), dpi=100),
    #               font_size=11,
    #               #y_lim={'new_infections': 500},
    #               legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
    #               axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
    #               fill_args={'alpha': 0.0},
    #               to_plot=['cum_infections'])
    
    # # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #               fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/Chicago-cum_deaths' + '.png',
    #               interval=30,
    #               fig_args=dict(figsize=(10, 5), dpi=100),
    #               font_size=11,
    #               #y_lim={'new_infections': 500},
    #               legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
    #               axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
    #               fill_args={'alpha': 0.0},
    #               to_plot=['cum_deaths'])
    

    # July30_release = sum(scens['Chicago'].results['new_infections']['lockdown relaxed by 10% on September 1']['best'][251:370])
    # print('Restrictions relaxed on September 1 =', July30_release)
    # July1_release = sum(scens['Chicago'].results['new_infections']['lockdown relaxed by 20% on October 1']['best'][251:370])
    # print('Restrictions relaxed on October 1 =', July1_release)