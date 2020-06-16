import user_interface as ui

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Manaus']
    # the name of the databook
    db_name = 'input_data_brazil'
    epi_name = 'epi_data_brazil'

    # country-specific parameters
    user_pars = {'Manaus': {'pop_size': int(10e4),
                               'beta': 0.05,
                               'n_days': 200}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Manaus': {'lockdown_1': {'beta': 0.2},
                              'lockdown_2': {'beta': 0.1}, 
                              'lockdown_3': {'beta': 0.1},
                              'relax_1': {'beta': 0.3}}}

    # Note that lockdown 3 comes into effect the first time at day 90
    
    # the policies to change during scenario runs
    # policy_change = {'Manaus': {'24 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
    #                                                     [[272]])},
    policy_change = {'Manaus': {'12 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
                                                        [[188]])},
                                '8 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
                                                        [[160]])}}}
                                # '12 week relax': {'replace': (['lockdown_3'], [['lockdown_2']], 
                                #                         [[174]])},
                                # '24 week relax': {'replace': (['lockdown_3'], [['lockdown_2']], 
                                #                         [[258]])}}}
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

    # ui.policy_plot(scens['Manaus'])
    ui.policy_plot(scens['Manaus'], to_plot={'Cumulative Deaths (Manaus)': 'cum_deaths'})
    ui.policy_plot(scens['Manaus'], to_plot={'Cumulative Diagnosis (Manaus)': 'cum_diagnoses'})
    ui.policy_plot(scens['Manaus'], to_plot={'Cumulative Infections (Manaus)': 'cum_infections'})
    ui.policy_plot(scens['Manaus'], to_plot={'New Daily Infections (Manaus)': 'new_infections'})
    # number of infections that occurred between day 100 and day 150
    infections = sum(scens['Manaus'].results['new_infections']['baseline']['best'][100:150])
    print(infections)
