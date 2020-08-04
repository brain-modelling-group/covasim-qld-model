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

# Add argument for number of runs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=5, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')
parser.add_argument('--randompop', default=True, type=bool, help='If True, generate a new population of people for each seed')  #

args = parser.parse_args()

# Load inputs
packages = outbreak.load_packages('packages.csv')
scenarios = outbreak.load_scenarios('scenarios.csv')
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=1, n_days=31)

if args.randompop:
    population = {'people': None, 'popdict': None}
else:
    people, popdict = co.make_people(params)
    population = {'people': people, 'popdict': popdict}

packages = {'relax_3':packages['relax_3'],'relax_4':['relax_4']}

for scen_name, scenario in scenarios.items():

    resultdir = Path(__file__).parent / f'results_{scen_name}'
    resultdir.mkdir(parents=True, exist_ok=True)

    params.test_prob = sc.mergedicts(params.test_prob, scenario)

    for name, policies in packages.items():

        if args.celery:
            # Run simulations using celery
            job = group([run_australia_outbreak.s(i, params, policies, **population) for i in range(args.nruns)])
            result = job.apply_async()

            with tqdm(total=args.nruns, desc=name) as pbar:
                while result.completed_count() < args.nruns:
                    time.sleep(1)
                    pbar.n = result.completed_count()
                    pbar.refresh()
                pbar.n = result.completed_count()
                pbar.refresh()
            sim_stats = result.join()
            result.forget()

        else:
            sim_stats = []
            for i in tqdm(range(args.nruns), desc=name):
                sim_stats.append(run_australia_outbreak(i, params, policies, **population))

        sc.saveobj(resultdir / f'{name}.stats', sim_stats)
