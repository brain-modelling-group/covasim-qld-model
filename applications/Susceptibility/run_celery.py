import sys
sys.path.append('../../')

from pathlib import Path
import outbreak
from outbreak.celery import run_australia_outbreak
from celery import group
import sciris as sc
from tqdm import tqdm

# Add argument for number of runs
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=10, type=int)
args = parser.parse_args()

# Load inputs
packages = outbreak.load_packages()
params = outbreak.load_australian_parameters('Victoria', pop_size=1e4, pop_infected=1, n_days=31)

for name, policies in packages.items():

    # Run simulations using celery
    job = group([run_australia_outbreak.s(i, params, policies) for i in range(args.nruns)])
    result = job.apply_async()
    sims = result.join()

    # Process and save outputs
    keep = [
        'cum_infections',
        'cum_diagnoses',
        'cum_deaths',
        'cum_quarantined',
    ]

    sim_stats = {}
    for quantity in keep:
        sim_stats[quantity] = [sim.results[quantity][-1] for sim in sims]

    sc.saveobj(Path(__file__).parent / f'{name}.stats', sim_stats)


#
#
#
#
# delayed_results = group_add.delay(l1, l2)
# delayed_results.get()  # Wait for parent task to be ready.
#
# results = []
# for result in tqdm(delayed_results.children[0], total=total):
#     results.append(result.get())
# print(results)