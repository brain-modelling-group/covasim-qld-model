import user_interface as ui
import utils
import os
dirname = os.path.dirname(__file__)

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Rio']
    # the name of the databook
    db_name = 'input_data_Brazil'
    epi_name = 'epi_data_Brazil'

    # Rioecify layer keys to use
    all_lkeys = ['H', 'S', 'W', 'C']
    dynamic_lkeys = ['C']  # layers which update dynamically (subset of all_lkeys)

    # country-Rioecific parameters
    user_pars = {'Rio': {'pop_size': int(10e4),
                               'beta': 0.094,
                               'n_days': 368,
                               'calibration_end': '2020-06-30'}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 8,
                'noise': 0.02,
                'verbose': 1,
                'rand_seed': 1}
    
    # the policies to change during scenario runs
    # scen_opts = {'Rio': {'No changes to current lockdown restrictions': 
    scen_opts = {'Rio': {'Small easing of restrictions on September 15': 
                              {'replace': (['lockdown2'], [['relax1']], [[202]]),
                              'policies': {'relax1': {'beta': 0.3}}},
                 
                            'Moderate easing of restrictions on September 15': 
                              {'replace': (['lockdown2'], [['relax2']], [[202]]),
                              'policies': {'relax2': {'beta': 0.4}}},
                 
                            'Small easing of restrictions on August 15': 
                              {'replace': (['lockdown2'], [['relax1']], [[171]]),
                              'policies': {'relax1': {'beta': 0.3}}},
                 
                            'Moderate easing of restrictions on August 15': 
                              {'replace': (['lockdown2'], [['relax2']], [[171]]),
                              'policies': {'relax2': {'beta': 0.4}}},
                 
                            'No changes to current lockdown restrictions': 
                              {'replace': (['lockdown2'], [['lockdown2']], [[120]]),
                              'policies': {'lockdown2': {'beta': 0.2}}}}}
                     
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

    new_no_release = sum(scens['scenarios']['Rio'].results['new_infections']['No changes to current lockdown restrictions']['best'][249:368])    
    new_september_smallrelease = sum(scens['scenarios']['Rio'].results['new_infections']['Small easing of restrictions on September 15']['best'][249:368])    
    new_september_moderaterelease = sum(scens['scenarios']['Rio'].results['new_infections']['Moderate easing of restrictions on September 15']['best'][249:368])    
    new_august_smallrelease = sum(scens['scenarios']['Rio'].results['new_infections']['Small easing of restrictions on August 15']['best'][249:368])
    new_august_moderaterelease = sum(scens['scenarios']['Rio'].results['new_infections']['Moderate easing of restrictions on August 15']['best'][249:368])
    cum_no_release = scens['scenarios']['Rio'].results['cum_infections']['No changes to current lockdown restrictions']['best'][368]
    cum_september_smallrelease = scens['scenarios']['Rio'].results['cum_infections']['Small easing of restrictions on September 15']['best'][368]
    cum_september_moderatelrelease = scens['scenarios']['Rio'].results['cum_infections']['Moderate easing of restrictions on September 15']['best'][368]
    cum_august_smallrelease = scens['scenarios']['Rio'].results['cum_infections']['Small easing of restrictions on August 15']['best'][368]
    cum_august_moderatelrelease = scens['scenarios']['Rio'].results['cum_infections']['Moderate easing of restrictions on August 15']['best'][368]
    cum_may18 = scens['scenarios']['Rio'].results['cum_infections']['No changes to current lockdown restrictions']['best'][81]  
    
    with open('Rio_projections.txt', 'w') as f:
        print('Sum of new infections Nov-Feb: No changes to current lockdown restrictions =', int(new_no_release), file=f)
        print('Sum of new infections Nov-Feb: Small easing of restrictions on September 15 =', int(new_september_smallrelease), file=f)
        print('Sum of new infections Nov-Feb: Moderate easing of restrictions on September 15 =', int(new_september_moderaterelease), file=f)
        print('Sum of new infections Nov-Feb: Small easing of restrictions on August 15 =', int(new_august_smallrelease), file=f)
        print('Sum of new infections Nov-Feb: Moderate easing of restrictions on on August 15 =', int(new_august_moderaterelease), file=f)
        print('Cumulative infections end of Feb: No changes to current lockdown restrictions =', int(cum_no_release), file=f)
        print('Cumulative infections end of Feb: Small easing of restrictions on September 15 =', int(cum_september_smallrelease), file=f)
        print('Cumulative infections end of Feb: Moderate easing of restrictions on September 15 =', int(cum_september_moderatelrelease), file=f)
        print('Cumulative infections end of Feb: Small easing of restrictions on August 15 =', int(cum_august_smallrelease), file=f)
        print('Cumulative infections end of Feb: Moderate easing of restrictions on on August 15 =', int(cum_august_moderatelrelease), file=f)
        print('Cumulative infections May 18 (baseline) =', int(cum_may18), file=f)
        f.close()
    
    # plot cumulative infections to see if all the population gets infected    
    utils.policy_plot2(scens, plot_ints=False, do_save=True, do_show=True,
                        fig_path=dirname + '/figs/Rio-projections' + '.png',
                  interval=30, n_cols=1,
                  fig_args=dict(figsize=(10, 5), dpi=100),
                  font_size=11,
                  #y_lim={'new_infections': 500},
                  legend_args={'loc': 'upper center', 'bbox_to_anchor': (0.5, -1.6)},
                  axis_args={'left': 0.1, 'wspace': 0.2, 'right': 0.95, 'hspace': 0.4, 'bottom': 0.3},
                  fill_args={'alpha': 0.3},
                  to_plot=['new_infections','cum_infections'])   