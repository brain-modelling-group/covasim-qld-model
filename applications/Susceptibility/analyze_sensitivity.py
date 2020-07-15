# Susceptibility distribution plots
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

resultsdir = Path(__file__).parent/'results_sensitivity'

# LOAD DATA INTO DATAFRAME
records = []
for statsfile in filter(lambda x: x.suffix=='.stats',resultsdir.iterdir()):
    print(f'Loading "{statsfile.stem}"')
    # stats[statsfile.stem] = sc.loadobj(statsfile)
    stats = sc.loadobj(statsfile)
    for d in stats:
        d['package'] = statsfile.stem
    records += stats
df = pd.DataFrame.from_records(records)
df.drop('package',axis=1,inplace=True) # Drop the package column

# PROBABILITY LANDSCAPE
n_crit = 100
g = df.groupby(['symp_prob', 'asymp_quar_prob'])

n_crit = 5000
g['cum_infections'].agg(lambda x: sum(x > n_crit))/g['cum_infections'].count()


df.groupby(['symp_prob', 'asymp_quar_prob'])



