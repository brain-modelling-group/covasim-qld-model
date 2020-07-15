# Susceptibility distribution plots
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

resultsdir = Path(__file__).parent/'results_sensitivity'

# resultsdir = Path(__file__).parent/'results_sensitivity_asymp_prob_0.05'

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
g = df.groupby(['symp_prob', 'asymp_quar_prob'])

x = g.mean()['cum_infections'].unstack(1)
print(x)


# symp_probs = np.linspace(0,1,6)
# asymp_quar_probs = np.linspace(0,1,6)
# y,x = np.meshgrid(symp_probs,asymp_quar_probs)
# #
#
# fig, ax = plt.subplots()
# c = ax.pcolor(x)
# fig.colorbar(c,ax=ax)
# #
# n_crit = 100
# g['cum_infections'].agg(lambda x: sum(x > n_crit))/g['cum_infections'].count()

#
# df.groupby(['symp_prob', 'asymp_quar_prob'])
#
# symp_probs = np.linspace(0,1,6)
# asymp_quar_probs = np.linspace(0,1,6)
#
