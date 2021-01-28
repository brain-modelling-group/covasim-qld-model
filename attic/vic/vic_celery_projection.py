# Main script to run scenarios

import numpy as np
from pathlib import Path
import resurgence
from resurgence.celery import resurgence_projection
from celery import group
import sciris as sc
from tqdm import tqdm
import time
import pandas as pd
import covasim_australia as cva
import functools
import covasim as cv
import shutil

# Clear the cache


# Add argument for number of runs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=4, type=int, help='Number of seeds to run per scenario')
parser.add_argument('--celery', default=False, type=bool, help='If True, use Celery for parallization')

args = parser.parse_args()

# Load inputs
people_seed = 1

print('Loading parameters...', end='')
sc.tic()
params = resurgence.get_victoria_params(pop_size=1e5)
print(f'done (took {sc.toc(output=True):.0f} s)')


# First, we need to build a collection of accepted beta values and calibration seeds
# We do this by reading the seeds from the summary spreadsheet
summary_values = sc.loadobj(Path('calibration_results')/'summary_values.obj')
calibration_seeds = [(beta, seed) for beta, seed, accepted in summary_values if accepted]

release_days = ['2020-09-14','2020-09-28', '2020-10-14']

if args.celery:

    resultsdir = Path('projection_results')
    resultsdir.mkdir(parents=True, exist_ok=True)

    # Sample from the calibration seeds. Use numpy sampling so that we are consistent with the RNG
    cv.set_seed(0)  # Set seed for beta generation
    x = np.empty(len(calibration_seeds), dtype=object)
    x[:] = calibration_seeds
    calibration_inputs = np.random.choice(x, args.nruns, replace=True)

    # Generate projection seeds
    projection_seeds = range(1, args.nruns+1)

    for release_day in release_days:
        (resultsdir / release_day).mkdir(parents=True, exist_ok=True)

        with tqdm(total=len(projection_seeds), desc=f'Release on {release_day}') as pbar:
            pbar.n = 0
            pbar.refresh()

            job = group([resurgence_projection.s(params, beta=beta, calibration_seed=calibration_seed, projection_seed=projection_seed, people_seed=people_seed, release_day=release_day) for (beta, calibration_seed), projection_seed in zip(calibration_inputs, projection_seeds)])
            result = job.apply_async()
            while result.completed_count() < args.nruns:
                time.sleep(1)
                pbar.n = result.completed_count()
                pbar.refresh()
            pbar.n = result.completed_count()
            pbar.refresh()

        outputs = result.join()
        result.forget()

        summary_rows = []
        for df, beta, calibration_seed, projection_seed, release_day in tqdm(outputs, desc="Saving CSV outputs"):
            summary_rows.append((beta, calibration_seed, projection_seed, release_day))
            df.to_csv(resultsdir/release_day /f'projection_{calibration_seed}_{projection_seed}_{release_day}.csv')

        df = pd.DataFrame(summary_rows,columns=['beta','calibration_seed','projection_seed','release_day'])
        df.to_csv(resultsdir / release_day /f'summary.csv')

else:
    resurgence_projection(params, 0.05891, calibration_seed=1, projection_seed=2, people_seed=people_seed, release_day=release_days[0])

