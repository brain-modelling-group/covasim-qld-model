import user_interface as ui
import pickle

if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['FS']
    # the name of the databook
    db_name = 'input_data_sa'

    # country-specific parameters
    user_pars = {'WC': {'pop_size': int(10e4),
                        'beta': 0.015,
                        'n_days': 339,
                        'pop_infected': 5000},
                 'GP': {'pop_size': int(10e4),
                        'beta': 0.032,
                        'n_days': 339,
                        'pop_infected': 1000},
                 'NW': {'pop_size': int(10e4),
                        'beta': 0.032,
                        'n_days': 339,
                        'pop_infected': 20},
                 'FS': {'pop_size': int(10e4),
                        'beta': 0.032,
                        'n_days': 339,
                        'pop_infected': 250},
                 'KZN': {'pop_size': int(10e4),
                        'beta': 0.032,
                        'n_days': 80,
                        'pop_infected': 1000},
                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'WC': {'lockdown_s5': {'beta': 1.45},
                          'lockdown_s4': {'beta': 1.2},
                          'lockdown_s3': {'beta': .9},
                          'lockdown_s5_v2': {'beta': .5}},
                   'GP': {'lockdown_s5': {'beta': .5},
                          'lockdown_s4': {'beta': .75},
                          'lockdown_s3': {'beta': 1.},
                          'lockdown_s5_v2': {'beta': .4}},
                   'NW': {'lockdown_s5': {'beta': .5},
                          'lockdown_s4': {'beta': .75},
                          'lockdown_s3': {'beta': 1.},
                          'lockdown_s5_v2': {'beta': .4}},
                   'FS': {'lockdown_s5': {'beta': .4},
                          'lockdown_s4': {'beta': .5},
                          'lockdown_s3': {'beta': 1.},
                          'lockdown_s5_v2': {'beta': .4}},
                   'KZN': {'lockdown_s5': {'beta': .35},
                          'lockdown_s4': {'beta': .35},
                          'lockdown_s3': {'beta': 1.},
                          'lockdown_s5_v2': {'beta': .4}},
                   }

    # Note that stage three comes into effect the first time at day 67

    # the policies to change during scenario runs
    policy_change = {'WC': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8*7, 67 + 8*7 + 10*7]])},
                            'Restrictions re-introduced Jul-Dec': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8 * 7, 67 + 8 * 7 + 20 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 16*7, 67 + 16*7 + 10*7]])}
                            },

                     'GP': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8 * 7, 67 + 8 * 7 + 10 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 16 * 7, 67 + 16 * 7 + 10 * 7]])}
                            },

                     'NW': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8 * 7, 67 + 8 * 7 + 10 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 16 * 7, 67 + 16 * 7 + 10 * 7]])}
                            },

                     'FS': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8 * 7, 67 + 8 * 7 + 10 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 15 * 7, 67 + 15 * 7 + 10 * 7]])}
                            },

                     'KZN': {'Restrictions re-introduced Jul-Oct': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 8 * 7, 67 + 8 * 7 + 10 * 7]])},
                            'Restrictions re-introduced Sep-Nov': {'replace': (['lockdown_s3'], [['lockdown_s5_v2']], [[67 + 16 * 7, 67 + 16 * 7 + 10 * 7]])}
                            },

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
    filehandler = open('runs/' + locations[0] + '.obj', 'wb')
    pickle.dump(scens, filehandler)

