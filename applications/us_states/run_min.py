import user_interface as ui
import plot


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Minesota']
    # the name of the databook
    db_name = 'input_data_min'
    epi_name = 'epi_data_min'

    # country-specific parameters
    user_pars = {'Minesota': {'pop_size': int(2e4),
                               'beta': 0.1,
                               'n_days': 100,
                          'pop_infected': 65}

                 }

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 1,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Minesota': {},
                   }
    # the policies to change during scenario runs

    policy_change = {'Minesota': {

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



    #PLOT
    scens_toplot = {'Minesota': ['baseline']}
    outcomes_toplot={'Cumulative deaths':'cum_deaths'}
    ui.policy_plot(scens, scens_toplot=scens_toplot, outcomes_toplot=outcomes_toplot)


