# Main script to run scenarios

import sys

sys.path.append('../../')

from pathlib import Path
import outbreak
from outbreak.celery import run_australia_outbreak
from celery import group
import sciris as sc
from tqdm import tqdm
import time
import contacts as co
import numpy as np
import data


# Load inputs
packages = outbreak.load_packages('packages.csv')[0]
scenarios = outbreak.load_scenarios('scenarios.csv')[0]
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=1, n_days=31)

db_name = 'input_data_Australia2'  # the name of the databook
epi_name = 'epi_data_Australia'

all_lkeys = ['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
             'transport', 'public_parks', 'large_events', 'child_care', 'social', 'aged_care']
dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events']

# return data relevant to each specified location in "locations"
all_data = data.read_data(locations=['Victoria'],
                          db_name=db_name,
                          epi_name=epi_name,
                          all_lkeys=all_lkeys,
                          dynamic_lkeys=dynamic_lkeys,
                          calibration_end=None)

policies = all_data['policies']
package_policies = set()
[package_policies.update(x) for x in packages.values()]

for policy in package_policies:
    print(policy)
    if policy in policies['beta_policies']:
        for layer, beta in policies['beta_policies'][policy].items():
            if beta < 1:
                print(f'- {layer} transmission reduced by {100*(1-beta):.0f}%')
            if beta >1:
                print(f'- {layer} transmission increased by {100*(beta-1):.0f}%')
    if policy in policies['clip_policies']:
        layers = policies['clip_policies'][policy]['layers']
        proportion = policies['clip_policies'][policy]['change']
        for layer in layers:
            print(f'- {layer} contacts decreased by {100*(1-proportion):.0f}%')
    print('\n')