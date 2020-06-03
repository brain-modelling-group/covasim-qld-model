# international
locations = ['Australia', 'New Zealand']
db_name = 'input_data'

all_pars = {'Australia': {'pop_size': int(2e4),
                          'beta': 0.05,
                          'n_days': 60},
            'New Zealand': {'pop_size': int(2e4),
                            'beta': 0.05,
                            'n_days': 60}}

metapars = {'n_runs': 2,
            'noise': 0,
            'verbose': 1,
            'rand_seed': 1}

policy_change = {'Australia': {'relax comm': {'replace': (['communication'], [['comm_relax']], [[20]])}},
                 'New Zealand': {'relax comm': {'replace': (['communication'], [['comm_relax']], [[20]])}}}



import data
db = data.load_databook('/Users/samwork/Documents/GitHub/covasim-australia/data_int/input_data.xlsx')
print(data.read_contact_matrix(locations, db))

