import user_interface as ui

# international
locations = ['Australia', 'New Zealand']
db_name = 'input_data'

user_pars = {'Australia': {'pop_size': int(2e4),
                          'beta': 0.05,
                          'n_days': 60},
            'New Zealand': {'pop_size': int(2e4),
                            'beta': 0.05,
                            'n_days': 60}}

metapars = {'n_runs': 2,
            'noise': 0,
            'verbose': 1,
            'rand_seed': 1}

policy_change = {'Australia': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[20]])}},
                 'New Zealand': {'relax lockdown': {'replace': (['lockdown'], [['lockdown_relax']], [[20]])}}}



scens = ui.setup_scens(locations=locations,
                       db_name=db_name,
                       epi_name='url',
                       policy_change=policy_change,
                       user_pars=user_pars,
                       metapars=metapars)

scens = ui.run_scens(scens)
