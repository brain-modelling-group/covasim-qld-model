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
packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=1, n_days=31)

if args.randompop:
    population = {'people': None, 'popdict': None}
else:
    people, popdict = co.make_people(params)
    population = {'people': people, 'popdict': popdict}

# for symp_prob in [0.01,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:

# Set up results directory
# resultdir = Path(__file__).parent / f'results_{symp_prob*100:03.0f}'
resultdir = Path(__file__).parent / f'results'
resultdir.mkdir(parents=True, exist_ok=True)

# import numpy as np
# np.seterr(all='raise')

scenarios = {
    'baseline':{
        'symp_prob': 0.1, # Probability of 0.1 means (1-0.9**14)~75% never test, which is in line with expectations
        'test_delay': 3 , # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1 , # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0, # Currently people are supposed to isolate while waiting
    },
    'more_testing': {
        'symp_prob': 0.1,  # Probability of 0.1 means (1-0.9**14)~75% never test, which is in line with expectations
        'test_delay': 3,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': np.inf,  # Do not require people to isolate while waiting for tests
    }
}


















params.test_prob['symp_prob'] = 0.1  # Someone who has symptoms has this probability of testing on any given day
params.test_prob['test_delay'] = 0  # Number of days for test results to be processed
params.test_prob['swab_delay'] = 0  # Number of days people wait after symptoms before being tested
params.test_prob['isolation_threshold'] = 0 # Isolate while waiting for test results if cum_diagnosed exceeds this amount

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
