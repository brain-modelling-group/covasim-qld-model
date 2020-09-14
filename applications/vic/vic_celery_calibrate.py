# Main script to run scenarios

import numpy as np
from pathlib import Path
import resurgence
from resurgence.celery import resurgence_calibration, stop_calibration
from celery import group
import sciris as sc
from tqdm import tqdm
import time
import pandas as pd
import covasim_australia as cva
import functools
import covasim as cv

# Add argument for number of runs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=4, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')

args = parser.parse_args()

# Load inputs

people_seed = 0

print('Loading parameters...', end='')
sc.tic()
params = resurgence.get_victoria_params(pop_size=1e5)
print(f'done (took {sc.toc(output=True):.0f} s)')

cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
params.pars['stopping_func'] = functools.partial(stop_calibration, cases=cases)


cv.set_seed(0)  # Set seed for beta generation
get_beta = lambda: np.around(np.random.normal(loc=0.006, scale=0.001), decimals=5) # Round to 5dp to facilitate reproducing results

if args.celery:

    resultsdir = Path('results')
    resultsdir.mkdir(parents=True, exist_ok=True)

    # If interrupted, start with a nonzero seed. However, we need to also discard any beta values
    # we've generated up to that point. So, first we determine what the last seed used was, then
    previous = 0
    for fname in resultsdir.rglob('calibration*.csv'):
        previous = max(previous, int(fname.stem.split('_')[-1]))
    print(f'Previous seed: {previous}')

    # Reset the seed then discard the required number of samples
    cv.set_seed(0)  # Set seed for beta generation
    betas = []
    for i in range(previous):
        get_beta()

    for i in range(args.nruns):
        betas.append(get_beta())
    seeds = range(previous+1, previous+args.nruns+1) # Start at 1. If we detect say, 10, then start at 11.

    assert len(betas) == len(seeds)

    with tqdm(total=len(seeds), desc=f'Calibration runs') as pbar:
        pbar.n = 0
        pbar.refresh()

        job = group([resurgence_calibration.s(params, beta, seed, people_seed=people_seed) for beta, seed in zip(betas, seeds)])
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

    summary = result.join()
    result.forget()

    df = pd.DataFrame(summary,columns=['beta','seed','accepted'])
    df.set_index('seed', inplace=True)

    # Try to get previous
    if (resultsdir/'summary.csv').exists():
        df2 = pd.read_csv(resultsdir/'summary.csv').set_index('seed')
        df = pd.concat([df, df2])
        df.index.name = 'seed'
    df.sort_index(inplace=True)
    df.to_csv(resultsdir/'summary.csv')

else:
    resurgence_calibration(params, 0.006, 0, people_seed=people_seed)

