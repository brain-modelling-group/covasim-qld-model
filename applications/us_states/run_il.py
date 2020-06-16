import user_interface as ui


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['IL']
    # the name of the databook
    db_name = 'input_data_il'
    epi_name = 'epi_data_il'

    # country-specific parameters
    user_pars = {'IL': {'pop_size': int(10e4),
                               'beta': 0.4,
                               'n_days': 80}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 2,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'IL': {'lockdown': {'beta': .5}}}

    # the policies to change during scenario runs
    policy_change = {'IL': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[20]])}}}

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

    # plot
    ui.policy_plot(scens, outcomes_toplot={'Cumulative Deaths': 'cum_deaths'},
                   scens_toplot={locations[0]: ['baseline']}, plot_ints=False)
    ui.policy_plot(scens, outcomes_toplot={'New Infections': 'new_infections'}, scens_toplot={locations[0]: ['baseline', 'relax lockdown']}, plot_ints=False)
