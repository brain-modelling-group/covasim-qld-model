# Susceptibility distribution plots
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

resultsdir = Path(__file__).parent/'results'

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

packages = df.loc[~df['package'].str.startswith('p_'),:]
policies = df.loc[df['package'].str.startswith('p_'),:]

# CRITICAL INFECTION SIZE BAR PLOT
fig, ax = plt.subplots()
order = None
levels = {50:'#ffbfbf',100:'#ff8585',250:'#c90000'}
for n, color in levels.items():
    p = packages.groupby('package')['cum_infections'].agg(lambda x: sum(x > n)) / packages.groupby('package')['cum_infections'].count()
    if order is None:
        order = p.argsort()
    p = p[order]
    p.plot.barh(ax=ax,color=color,label=f'> {n}')
plt.legend()
plt.ylabel(None)
plt.xlabel('Probability')
plt.xlim(0,1)
ax.invert_yaxis()
plt.title('Probability of outbreak size')
fig.set_size_inches(16, 7)
fig.savefig(resultsdir / 'probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

# BOXPLOT OF INFECTION SIZE
fig, ax = plt.subplots()
grouped = packages.reset_index().groupby(['package'])
df2 = pd.DataFrame({col:vals['cum_infections'] for col,vals in grouped})
means = df2.mean()
means.sort_values(ascending=True, inplace=True)
df2 = df2[means.index]
df2.boxplot()
fig.set_size_inches(16, 7)
plt.ylabel('Total number of infections')
fig.savefig(resultsdir / 'infection_size.png', bbox_inches='tight', dpi=300, transparent=False)

# EFFECTIVENESS OF EACH POLICY
fig, ax = plt.subplots()
baseline = packages.groupby('package').mean().loc['No policies']
mean_outcome = policies.groupby('package').mean()
reduction = 100*(baseline-mean_outcome)/baseline
reduction = reduction.sort_values(by='cum_infections')
reduction['cum_infections'].plot.barh()
plt.title('Relative impact of individual policies')
fig.set_size_inches(14, 10)
plt.xlabel('Reduction in average outbreak size (%)')
plt.axvline(0,color='k')
fig.savefig(resultsdir / 'individual_policies.png', bbox_inches='tight', dpi=300, transparent=False)

# PROBABILITY OF CONTAINING INFECTION WITHIN 30 DAYS
contained = 0.8*packages.set_index('package')['peak_infections']>packages.set_index('package')['active_infections']
p = contained.groupby('package').sum()/contained.groupby('package').count()
p = p.sort_values()
fig, ax = plt.subplots()
p.plot.barh()
plt.ylabel(None)
plt.xlabel('Probability')
plt.xlim(0,1)
ax.invert_yaxis()
plt.title('Probability of containing outbreak without policy change')
fig.set_size_inches(16, 7)
fig.savefig(resultsdir / 'containment_probability.png', bbox_inches='tight', dpi=300, transparent=False)

# ACTIVE INFECTION CONTACT TRACING LIMITS
fig, ax = plt.subplots()
order = None
levels = {50:'#ffbfbf',100:'#ff8585',250:'#c90000'}
for n, color in levels.items():
    p = packages.groupby('package')['peak_infections'].agg(lambda x: sum(x > n)) / packages.groupby('package')['peak_infections'].count()
    if order is None:
        order = p.argsort()
    p = p[order]
    p.plot.barh(ax=ax,color=color,label=f'> {n}')
plt.legend()
plt.ylabel(None)
plt.xlabel('Probability')
plt.xlim(0,1)
ax.invert_yaxis()
plt.title('Probability of simultaneous active infections')
fig.set_size_inches(16, 7)
fig.savefig(resultsdir / 'tracing_capacity_probability.png', bbox_inches='tight', dpi=300, transparent=False)