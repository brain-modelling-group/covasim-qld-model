import user_interface as ui
import utils
import os

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['New Orleans']
    # the name of the databook
    db_name = 'input_data_US'
    epi_name = 'epi_data_US'

    # country-specific parameters
    user_pars = {'New Orleans': {'pop_size': int(10e4),
                               'beta': 0.051,
                               'n_days': 370}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}
    
    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'New Orleans': {'lockdown1': {'beta': 0.6},
                              'lockdown2': {'beta': 0.3}, 
                              'lockdown3': {'beta': 0.2},
                              'relax1': {'beta': 0.3}, 
                              'relax2': {'beta': 0.4},
                              'relax3': {'beta': 0.5}, 
                              'relax4': {'beta': 0.8},
                              'relax5': {'beta': 0.9}}}
    
    # the policies to change during scenario runs
    # policy_change = {'New Orleans': {'lockdown restrictions relaxed by 20% on July 30': {'replace': (['relax3'], [['lockdown1']], 
    #                                                     [[157]])}}}
    policy_change = {'New Orleans': {'lockdown restrictions eased by 40% on August 30': {'replace': (['relax3'], [['relax4']], 
                                                        [[174]])},
                                     'lockdown restrictions easded by 30% August 15': {'replace': (['relax3'], [['relax4']], 
                                                        [[159]])}}}
                     
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
    dirname = os.path.dirname(__file__)
    
    # plot cumulative deaths for calibration
    # utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
    #               fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/New-Orleans-calibration' + '.png',
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
                  fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/New-Orleans-new_diag' + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
                  fill_args={'alpha': 0.0},
                  to_plot=['new_diagnoses'])
    
    # # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                  fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/New-Orleans-cum_inf' + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
                  fill_args={'alpha': 0.0},
                  to_plot=['cum_infections'])
    
    # plot new infections, data of interest
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path='C:/Users/farah.houdroge/Documents/Covid/covasim-australia-feature-international/figures/US' + '/New-Orleans-new_inf' + '.png',
                  interval=30,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.1)},
                  axis_args={'left': 0.1, 'right': 0.9, 'bottom': 0.25},
                  fill_args={'alpha': 0.0},
                  to_plot=['new_infections'])
    

    July30_release = sum(scens['New Orleans'].results['new_infections']['lockdown restrictions eased by 40% on August 30']['best'][251:370])
    print('Restrictions relaxed on August 16 40% =', July30_release)
    July1_release = sum(scens['New Orleans'].results['new_infections']['lockdown restrictions easded by 30% August 15']['best'][251:370])
    print('Restrictions relaxed on August 15 30% =', July1_release)