import sys

sys.path.append('../../')

from pathlib import Path
import outbreak
from outbreak.celery import run_australia_test_prob
from celery import group
import sciris as sc
from tqdm import tqdm
import time
import numpy as np


# Add argument for number of runs
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=10, type=int)
parser.add_argument('--celery', default=False, type=bool)
args = parser.parse_args()

# Set up results directory
resultdir = Path(__file__).parent / 'results_sensitivity'
resultdir.mkdir(parents=True, exist_ok=True)

# Load inputs
packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, pop_infected=1, n_days=31)

symp_probs = np.linspace(0,1,6)
asymp_quar_probs = np.linspace(0,1,6)
name = 'Pre outbreak'
policies = packages['Pre outbreak']

for i, symp_prob in enumerate(symp_probs):
    for j, asymp_quar_prob in enumerate(asymp_quar_probs):

        if args.celery:
            # Run simulations using celery
            job = group([run_australia_test_prob.s(i, params, policies, symp_prob=symp_prob, asymp_prob=0.01, symp_quar_prob=0.95, asymp_quar_prob=asymp_quar_prob) for i in range(args.nruns)])
            result = job.apply_async()

            with tqdm(total=args.nruns, desc=f'{symp_prob}:{asymp_quar_prob}') as pbar:
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
            for i in tqdm(range(args.nruns), desc=f'{symp_prob}:{asymp_quar_prob}'):
                sim_stats.append(run_australia_test_prob(i, params, policies, symp_prob, asymp_quar_prob))

        sc.saveobj(resultdir / f'{name}_{i}_{j}.stats', sim_stats)
