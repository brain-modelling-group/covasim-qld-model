# Main script to run scenarios

import sys

sys.path.append('../../')

from pathlib import Path
import outbreak
from outbreak.celery import run_australia_outbreak, stop_sim_scenarios
from celery import group
import sciris as sc
from tqdm import tqdm
import time
import concurrent.futures
import threading

# Add argument for number of runs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=4, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')

args = parser.parse_args()

# Load inputs
packages = outbreak.load_packages('relax_packages.csv')[0]
scenarios = outbreak.load_scenarios('relax_scenarios.csv')[0]

print('Loading parameters...', end='')
sc.tic()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e5, n_infected=1, n_days=31)
print(f'done (took {sc.toc(output=True):.0f} s)')

# def stop_sim(sim):
#     return (sim.t > 7)
#     return (sim.t > 7 and sim.results['new_diagnoses'][sim.t-1] > 50)
#
params.pars['stopping_func'] = stop_sim_scenarios

thread_local = threading.local()

def run_scenario(n_infections, scen_name, package_name):
    savefile = Path(__file__).parent / 'relax' / f'{scen_name}' / f'{package_name}_{n_infections}.stats'
    savefile.parent.mkdir(parents=True, exist_ok=True)

    scenario = scenarios[scen_name]
    policies = packages[package_name]

    local_params = sc.dcp(params)
    local_params.test_prob = sc.mergedicts(local_params.test_prob, scenario)
    local_params.seed_infections = {1: n_infections}

    if args.celery:
        if not hasattr(thread_local,'pbar'):
            thread_local.pbar = tqdm(total=args.nruns)
        pbar = thread_local.pbar
        pbar.set_description(f'{scen_name}-{package_name}-{n_infections}')
        pbar.n = 0
        pbar.refresh()

        if savefile.exists():
            return

        # Run simulations using celery
        job = group([run_australia_outbreak.s(i, local_params, policies) for i in range(args.nruns)])
        result = job.apply_async()
        while result.completed_count() < args.nruns:
            time.sleep(1)
            pbar.n = result.completed_count()
            if pbar.n == 0:
                pbar.reset(total=args.nruns)
            else:
                pbar.refresh()
        pbar.n = result.completed_count()
        pbar.refresh()
        sim_stats = result.join()
        result.forget()
    else:
        sim_stats = []
        for i in tqdm(range(args.nruns), desc=f'{scen_name}-{package_name}-{n_infections}'):
            sim_stats.append(run_australia_outbreak(i, sc.dcp(local_params), sc.dcp(policies)))
    sc.saveobj(savefile, sim_stats)


to_check = [1, 5, 10, 25, 50]

if args.celery:
    futures = []

    with tqdm(total=len(to_check)*len(scenarios)*len(packages), desc=f'Total progress') as pbar:
        pbar.n = 0
        pbar.refresh()

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for n_infections in to_check:
                for scen_name, scenario in scenarios.items():
                    for package_name, policies in packages.items():
                        futures.append(executor.submit(run_scenario, n_infections, scen_name, package_name))
                        time.sleep(1)

            while True:
                states = [x.done() for x in futures]
                pbar.n = sum(states)
                pbar.refresh()
                if all(states):
                    break
                time.sleep(1)

            for res in futures:
                exception = res.exception()
                if exception:
                    print(exception)

else:
    for n_infections in to_check:
        for scen_name, scenario in scenarios.items():
            for package_name, policies in packages.items():
                run_scenario(n_infections, scen_name, package_name)
