import sys

sys.path.append('../../')

from pathlib import Path
import outbreak
from outbreak.celery import run_australia_outbreak
from celery import group
import sciris as sc
from tqdm import tqdm
import time

# Add argument for number of runs
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=10, type=int)
parser.add_argument('--celery', default=False, type=bool)
args = parser.parse_args()

# Set up results directory
resultdir = Path(__file__).parent / 'results'
resultdir.mkdir(parents=True, exist_ok=True)

# Load inputs
packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, pop_infected=1, n_days=31)

use_celery = True

for name, policies in packages.items():

    if args.celery:
        # Run simulations using celery
        job = group([run_australia_outbreak.s(i, params, policies) for i in range(args.nruns)])
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
            sim_stats.append(run_australia_outbreak(i, params, policies))

    sc.saveobj(resultdir / f'{name}.stats', sim_stats)
