import user_interface as ui


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Rio de Janerio']
    # the name of the databook
    db_name = 'input_data_brazil'
    epi_name = 'epi_data_brazil'

    # country-specific parameters
    user_pars = {'Rio de Janerio': {'pop_size': int(20e4),
                               'beta': 0.1,
                               'n_days': 90}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 2,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Rio de Janerio': {'lockdown': {'beta': .2}}}

    # the policies to change during scenario runs
    policy_change = {'Rio de Janerio': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[60]])}}}

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

    ui.policy_plot(scens['Rio de Janerio'])
