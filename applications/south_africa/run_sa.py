import user_interface as ui


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['WC']
    # the name of the databook
    db_name = 'input_data_sa'

    # country-specific parameters
    user_pars = {'WC': {'pop_size': int(10e4),
                               'beta': 0.1,
                               'n_days': 365,
                        'pop_infected': 5000},
                 'NW': {'pop_size': int(10e4),
                        'beta': 0.1,
                        'n_days': 100,
                        'pop_infected': 5}
                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'WC': {'lockdown_s5': {'beta': .2},
                          'lockdown_s4': {'beta': .3},
                          'lockdown_s3': {'beta': .4}},
                   'NW': {'lockdown_s5': {'beta': .2},
                          'lockdown_s4': {'beta': .3},
                          'lockdown_s3': {'beta': .4}}
                   }

    # the policies to change during scenario runs
    policy_change = {'WC': {'4 week relax': {'replace': (['lockdown_s3'], [['lockdown_s5']], [[92]])},
                     '2 week relax': {'replace': (['lockdown_s3'], [['lockdown_s5']], [[79]])},
                     'No relax': {'replace': (['lockdown_s3'], [['lockdown_s5']], [[67]])}},
                     'NW': {'4 week relax': {'replace': (['lockdown_s3'], [['lockdown_s5']], [[92]])}}
                     }

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name='epi_data_sa',
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    # run the scenarios
    scens = ui.run_scens(scens)

    ui.policy_plot(scens['WC'])

