from pathlib import Path

import covasim as cv
import pandas as pd

import contacts as co
import data
import parameters
import policy_updates
import sciris as sc
import utils
import functools
import numpy as np
import sys

from covasim import misc
misc.git_info = lambda: None  # Disable this function to increase performance slightly


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ncpus',default=2,type=int)
    args = parser.parse_args()
    print(args)

    n_runs = 2
    n_days = 31
    pop_size = 1e4
    pop_infected = 1 # Number of initial infections
    rootdir = Path(__file__).parent



    for name, policies in packages.items():
        with sc.Timer(label=f'Scenario "{name}"') as t:

            sim_fcn = functools.partial(run_australia_outbreak, params=params, scen_policies=policies)

            print('Running simulations...')
            sims = sc.parallelize(sim_fcn, np.arange(n_runs),ncpus=args.ncpus)
            print('Saving output...')

            # sc.saveobj(rootdir/f'{name}.sims', sims)
            # cova_scen.save()

            keep = [
                'cum_infections',
                'cum_diagnoses',
                'cum_deaths',
                'cum_quarantined',
            ]

            sim_stats = {}
            for quantity in keep:
                sim_stats[quantity] = [sim.results[quantity][-1] for sim in sims]

            sc.saveobj(rootdir/f'{name}.stats', sim_stats)
