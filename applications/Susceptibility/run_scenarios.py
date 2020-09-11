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
parser.add_argument('--nruns', default=100, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')

args = parser.parse_args()

# Load inputs
packages = outbreak.load_packages('packages.csv')[0]
scenarios = outbreak.load_scenarios('scenarios.csv')[0]


print('Loading parameters...', end='')
sc.tic()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=1, n_days=31)
print(f'done (took {sc.toc(output=True):.0f} s)')

params.pars['stopping_func'] = stop_sim_scenarios

thread_local = threading.local()

people_seed = 1

def run_scenario(scen_name, package_name):

    scenario = scenarios[scen_name]
    policies = packages[package_name]

    # Extract tracing
    testing = {k.replace('testing_','',1):v for k,v in scenario.items() if k.startswith('testing_')}
    trace_probs = {k.replace('trace_prob_','',1):v for k,v in scenario.items() if k.startswith('trace_prob_')}
    trace_time = {k.replace('trace_time_','',1):v for k,v in scenario.items() if k.startswith('trace_time_')}

    local_params = sc.dcp(params)
    local_params.test_prob = sc.mergedicts(local_params.test_prob, testing)
    local_params.extrapars['trace_probs'] = sc.mergedicts(local_params.extrapars['trace_probs'], trace_probs)
    local_params.extrapars['trace_time'] = sc.mergedicts(local_params.extrapars['trace_time'], trace_time)

    if args.celery:
        if not hasattr(thread_local,'pbar'):
            thread_local.pbar = tqdm(total=args.nruns)
        pbar = thread_local.pbar
        pbar.set_description(f'{scen_name}-{package_name}')
        pbar.n = 0
        pbar.refresh()

        savefile = Path(__file__).parent / 'scenarios' / f'{scen_name}' / f'{package_name}.stats'
        savefile.parent.mkdir(parents=True, exist_ok=True)
        if savefile.exists():
            return

        # Run simulations using celery
        job = group([run_australia_outbreak.s(i, local_params, policies, people_seed=people_seed) for i in range(args.nruns)])
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
        sc.saveobj(savefile, sim_stats)
        result.forget()
    else:
        sim_stats = []
        for i in tqdm(range(args.nruns), desc=f'{scen_name}-{package_name}'):
            sim_stats.append(run_australia_outbreak(i, sc.dcp(local_params), sc.dcp(policies), people_seed=people_seed))


if args.celery:
    futures = []

    with tqdm(total=len(scenarios)*len(packages), desc=f'Total progress') as pbar:
        pbar.n = 0
        pbar.refresh()

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for scen_name, scenario in scenarios.items():
                for package_name, policies in packages.items():
                    futures.append(executor.submit(run_scenario, scen_name, package_name))
                    # time.sleep(1)

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
    # for scen_name, scenario in scenarios.items():
    #     for package_name, policies in packages.items():
    run_scenario('best_case_tracing', 'relax_4_nomasks')

