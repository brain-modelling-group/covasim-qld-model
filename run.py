import os
import setup

# file path
root = os.path.dirname(os.path.abspath(__file__))

# create data object
setting = 'victoria'
file_name = 'vic-data'

pars = {'beta': 0.11, 'n_days': 60}
metapars = {'noise': 0, 'n_runs': 10}

setup.setup(root, file_name, setting, pars=pars, metapars=metapars)
