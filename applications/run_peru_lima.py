import user_interface as ui
import plot


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Lima']
    # the name of the databook
    db_name = 'input_data_peru'
    epi_name = 'epi_data_peru'

    # country-specific parameters
    user_pars = {'Lima': {'pop_size': int(2e4),
                               'beta': 0.1,
                               'n_days': 365,
                          'pop_infected': 65}

                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Lima': {'lockdown': {'beta': 0.3},
                              'heavy_lockdown': {'beta': 0.15},
                              'phase_1': {'beta': 0.15},
                              'phase_2': {'beta': 0.5},
                              'phase_3': {'beta': 0.19},
                              'phase_4': {'beta': 0.8}},
                   }
    # the policies to change during scenario runs

    policy_change = {'Lima': {'5% of restrictions lifted in August': {'replace': (['heavy_lockdown'], [['phase_3']], [[150]])},
                            '5% of restrictions lifted in November': {'replace': (['heavy_lockdown'], [['phase_3']], [[243]])},

    }}
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

    #PRINT INFECTIONS IN NOV-FEB
    infections_base = sum(scens['Lima'].results['new_infections']['baseline']['best'][243:363])
    print('infections base =', infections_base)


    August_release = sum(scens['Lima'].results['new_infections']['5% of restrictions lifted in August']['best'][243:363])
    print('5% of restrictions lifted in August =',August_release)
    November_release = sum(scens['Lima'].results['new_infections']['5% of restrictions lifted in November']['best'][243:363])
    print('5% of restrictions lifted in November  =', November_release)

    #PLOT
    scens_toplot = {'Lima': ['baseline','5% of restrictions lifted in August','5% of restrictions lifted in November']}
    outcomes_toplot={'New infections':'new_infections'}
    ui.policy_plot(scens, scens_toplot=scens_toplot, outcomes_toplot=outcomes_toplot)


