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
import concurrent.futures

# Add argument for number of runs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=4, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')

args = parser.parse_args()

# Load inputs
packages = outbreak.load_packages('./relax/packages.csv')[0]
scenarios = outbreak.load_scenarios('./relax/scenarios.csv')[0]
params = outbreak.load_australian_parameters('Victoria', pop_size=5e4, n_infected=1, n_days=31)

def run_scenario(n_infections, scen_name, package_name, offset=0):
    savefile = Path(__file__).parent / 'relax' / f'{scen_name}' / f'{package_name}_{n_infections}.stats'
    savefile.parent.mkdir(parents=True, exist_ok=True)

    scenario = scenarios[scen_name]
    policies = packages[package_name]

    local_params = sc.dcp(params)
    local_params.test_prob = sc.mergedicts(local_params.test_prob, scenario)
    local_params.seed_infections = {1: n_infections}

    if args.celery:

        if savefile.exists():
            return

        # Run simulations using celery
        job = group([run_australia_outbreak.s(i, local_params, policies) for i in range(args.nruns)])
        result = job.apply_async()
        with tqdm(total=args.nruns, desc=f'{scen_name}-{package_name}-{n_infections}', position=offset) as pbar:
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
        for i in tqdm(range(args.nruns), desc=f'{scen_name}-{package_name}', position=offset):
            sim_stats.append(run_australia_outbreak(i, sc.dcp(local_params), sc.dcp(policies)))
    sc.saveobj(savefile, sim_stats)


to_check = [1, 5, 10, 25, 50]

if args.celery:
    offset = 0
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for n_infections in to_check:
            for scen_name, scenario in scenarios.items():
                for package_name, policies in packages.items():
                    futures.append(executor.submit(run_scenario, n_infections, scen_name, package_name, offset))
                    time.sleep(1)
                    offset += 1
else:
    for n_infections in to_check:
        for scen_name, scenario in scenarios.items():
            for package_name, policies in packages.items():
                run_scenario(n_infections, scen_name, package_name, 0)
