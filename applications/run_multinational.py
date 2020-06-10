import user_interface as ui


if __name__ == "__main__":
    # the list of locations for this analysis
    locations = ['Australia', 'New Zealand']
    # the name of the databook
    db_name = 'input_data'

    # country-specific parameters
    user_pars = {'Australia': {'pop_size': int(2e4),
                               'beta': 0.05,
                               'n_days': 60},
                'New Zealand': {'pop_size': int(2e4),
                                'beta': 0.05,
                                'n_days': 60}}

    # the metapars for all countries and scenarios
    metapars = {'n_runs': 2,
                'noise': 0,
                'verbose': 1,
                'rand_seed': 1}

    # if required, change the each policy beta, date_implemented & date_ended
    policy_vals = {'Australia': {'lockdown': {'beta': .5}}}

    # the policies to change during scenario runs
    policy_change = {'Australia': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[20]])}},
                     'New Zealand': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[20]])}}}

    # set up the scenarios
    scens = ui.setup_scens(locations=locations,
                           db_name=db_name,
                           epi_name='url',
                           policy_change=policy_change,
                           user_pars=user_pars,
                           metapars=metapars,
                           policy_vals=policy_vals)
    # run the scenarios
    scens = ui.run_scens(scens)

    ui.policy_plot(scens['Australia'])
