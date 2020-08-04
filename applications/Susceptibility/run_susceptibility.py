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
packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, n_infected=1, n_days=31)

if args.randompop:
    population = {'people': None, 'popdict': None}
else:
    people, popdict = co.make_people(params)
    population = {'people': people, 'popdict': popdict}


scenarios = {
    'baseline': { # Resembles current policies
        'symp_prob': 0.1, # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 3 , # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1 , # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0, # Currently people are supposed to isolate while waiting
        'leaving_quar_prob': 0, # Not required to test if known contact
    },
    'no_isolation': { # If people don't need to isolate, they're more likely to test
        'symp_prob': 0.4, # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 3 , # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1 , # Number of days people wait after symptoms before being tested
        'isolation_threshold': np.inf, # Currently people are supposed to isolate while waiting
    },
    'faster_results': {  # Process tests 1 day faster
        'symp_prob': 0.25, # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 2 , # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1 , # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0, # Currently people are supposed to isolate while waiting
    },
    'faster_swabs': {  # Encourage people to get tested earlier
        'symp_prob': 0.25,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 3,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 0,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0,  # Currently people are supposed to isolate while waiting
    },
    'slower_results': {  # Process tests 1 day slower
        'symp_prob': 0.25,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 4,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0,  # Currently people are supposed to isolate while waiting
    },
    'slower_swabs': {  # People wait longer to get tested
        'symp_prob': 0.25,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 3,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 2,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': 0,  # Currently people are supposed to isolate while waiting
    },
    'non_compliant_iso': {  # People don't isolate
        'symp_prob': 0.25,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 3,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 1,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': np.inf,  # Currently people are supposed to isolate while waiting
    },
    'ideal': {  # Fast swab and fast tests with no isolation
        'symp_prob': 0.4,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 1,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 0,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': np.inf,  # Currently people are supposed to isolate while waiting
    },
    'ideal_trigger_20': {  # Ideal, but add isolation back once 20 cases have been diagnosed
        'symp_prob': 0.4,  # Based on ~60% of cases being asymptomatic, and 10x as many infections as diagnosed, implying 25% of symptomatic cases get diagnosed
        'symp_quar_prob': 0.8,  # Assume 80% of people told to quarantine will go for testing
        'test_delay': 1,  # Number of days for test results to be processed. It could be worse, or could be better
        'swab_delay': 0,  # Number of days people wait after symptoms before being tested
        'isolation_threshold': 20,  # Currently people are supposed to isolate while waiting
    },
}

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
