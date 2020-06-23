import user_interface as ui


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Australia']
    # the name of the databook
    db_name = 'input_data_countryX'
    epi_name = 'epi_data_countryX'

    # country-specific parameters
    user_pars = {'Australia': {'pop_size': int(2e4),
                               'beta': 0.2,
                               'n_days': 60},
                 'New Zealand': {'pop_size': int(2e4),
                               'beta': 0.2,
                               'n_days': 60}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 2,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    scen_opts = {'Australia': {'relax lockdown': {'replace':  (['lockdown'], [['lockdown_relax']], [[20]]),
                                                  'policies': {'lockdown': {'beta_rr': 0.6, 'H': 0.5}},
                                                  'tracing_policies': {'tracing_app': {'coverage': [0.2, 0.4], 'days': [14, 20], 'banana':1},
                                                                       'id_checks': {'coverage': [0.2, 0.4], 'days': [14, 20]}}}}}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name=epi_name,
                           scen_opts=scen_opts,
                           user_pars=user_pars,
                           metapars=metapars)
    # run the scenarios
    scens = ui.run_scens(scens)

    # plot
    # scens_toplot = {'Australia': ['baseline', 'relax lockdown', 'turn off lockdown'],
    #                 'New Zealand': ['baseline', 'relax lockdown']}
    # outcomes_toplot = {'Cumulative infections': 'cum_infections',
    #                    'New infections': 'new_infections',
    #                    'Cumulative deaths': 'cum_deaths'}
    # ui.policy_plot(scens, scens_toplot=scens_toplot, outcomes_toplot=outcomes_toplot)
