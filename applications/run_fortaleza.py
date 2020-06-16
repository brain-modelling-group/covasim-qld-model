import user_interface as ui

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Fortaleza']
    # the name of the databook
    db_name = 'input_data_brazil'
    epi_name = 'epi_data_brazil'

    # country-specific parameters
    user_pars = {'Fortaleza': {'pop_size': int(10e4),
                               'beta': 0.1,
                               'n_days': 365}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Fortaleza': {'lockdown_1': {'beta': 0.2},
                              'lockdown_2': {'beta': 0.15}, 
                              'lockdown_3': {'beta': 0.1},
                              'relax_1': {'beta': 0.1}}}

    # Note that lockdown 3 comes into effect the first time at day 90
    
    # the policies to change during scenario runs
    # policy_change = {'Fortaleza': {'24 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
    #                                                     [[272]])},
    policy_change = {'Fortaleza': {'16 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
                                                        [[216]])},
                                '8 week relax': {'replace': (['lockdown_3'], [['relax_1']], 
                                                        [[160]])}}
                     }
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

    # ui.policy_plot(scens['Fortaleza'])
    ui.policy_plot(scens['Fortaleza'], to_plot={'Cumulative Deaths (Fortaleza)': 'cum_deaths'})
    ui.policy_plot(scens['Fortaleza'], to_plot={'Cumulative Diagnosis (Fortaleza)': 'cum_diagnoses'})
    ui.policy_plot(scens['Fortaleza'], to_plot={'Cumulative Infections (Fortaleza)': 'cum_infections'})
    ui.policy_plot(scens['Fortaleza'], to_plot={'New Daily Infections (Fortaleza)': 'new_infections'})


    # number of infections that occurred between November and February
    infections2 = sum(scens['Fortaleza'].results['new_infections']['16 week relax']['best'][234:354])
    print(infections2)
    infections3 = sum(scens['Fortaleza'].results['new_infections']['8 week relax']['best'][234:354])
    print(infections3)
    