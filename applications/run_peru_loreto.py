import user_interface as ui
import plot


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Loreto']#,'Callao']
    # the name of the databook
    db_name = 'input_data_peru1'
    epi_name = 'epi_data_peru1'

    # country-specific parameters
    user_pars = {'Loreto': {'pop_size': int(10e4),
                               'beta': 0.12,
                               'n_days': 365,
                                'pop_infected': 150}

                 }#,'Callao': {'pop_size': int(2e4),'beta': 0.4,'n_days': 250}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 3,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Loreto': {'lockdown': {'beta': 0.4},
                              'heavy_lockdown': {'beta': 0.2},
                              'phase_1': {'beta': 0.25},
                              'phase_2': {'beta': 0.5},
                              'phase_3': {'beta': 0.4},
                              'phase_4': {'beta': 0.3}},
                   }
    # the policies to change during scenario runs

    policy_change = {'Loreto': {#'early relax 50%': {'replace': (['phase_1'], [['phase_2']], [[100]])},
                                'On time relax 50%': {'replace': (['phase_1'], [['phase_2']], [[150]])},
                                'Late relax 50%': {'replace': (['phase_1'], [['phase_2']], [[250]])},
                                #'early relax 30%': {'replace': (['phase_1'], [['phase_3']], [[100]])},
                                'On time relax 40%': {'replace': (['phase_1'], [['phase_3']], [[150]])},
                                'Late relax 40%': {'replace': (['phase_1'], [['phase_3']], [[250]])},
                                #'early relax 40%': {'replace': (['phase_1'], [['phase_4']], [[100]])},
                                #'on time relax 30%': {'replace': (['phase_1'], [['phase_4']], [[150]])},
                                #'Late relax 30%': {'replace': (['phase_1'], [['phase_4']], [[250]])},
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

    infections_base = sum(scens['Loreto'].results['new_infections']['baseline']['best'][243:363])
    print('infections base =', infections_base)

    infections_ontime50 = sum(scens['Loreto'].results['new_infections']['On time relax 50%']['best'][243:363])
    print('infections on time relax 50% =',infections_ontime50)
    infections_late50 = sum(scens['Loreto'].results['new_infections']['Late relax 50%']['best'][243:363])
    print('infections late relax 50% =', infections_late50)

    infections_ontime40 = sum(scens['Loreto'].results['new_infections']['On time relax 40%']['best'][243:363])
    print('infections on time relax 40% =',infections_ontime40)
    infections_late40 = sum(scens['Loreto'].results['new_infections']['Late relax 40%']['best'][243:363])
    print('infections Late 40% relax =', infections_late40)

    # infections_ontime30 = sum(scens['Lima'].results['new_infections']['on time relax 30%']['best'][243:363])
    # print('infections on time relax 30% =',infections_ontime30)
    # infections_late30 = sum(scens['Lima'].results['new_infections']['Late relax 30%']['best'][243:363])
    # print('infections Late relax 30%  =', infections_late30)


    ui.policy_plot(scens['Loreto'])
    ui.policy_plot(scens['Loreto'], to_plot={'New Infections':'new_infections'})
    #ui.policy_plot(scens['Callao'])
