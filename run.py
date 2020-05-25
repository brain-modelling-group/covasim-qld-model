import os
import setup

# file path
root = os.path.dirname(os.path.abspath(__file__))

# create data object
setting = 'victoria'
file_name = 'vic-data'
epidata_name = 'data/vic-epi-data.xlsx'

pars = {'beta': 0.11, 'n_days': 60}
metapars = {'n_runs': 10,
            'noise': 0}

setup.setup(root=root,
            databook_name=file_name,
            epidata_name=epidata_name,
            setting=setting,
            pars=pars,
            metapars=metapars)
