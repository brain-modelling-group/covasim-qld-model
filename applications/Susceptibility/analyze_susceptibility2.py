# Susceptibility distribution plots
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

for symp_prob in [0.01,0.05,0.1,0.15,0.2,0.3,0.4,0.5,0.75,1.0]:

    resultdir = Path(__file__).parent / f'results_{symp_prob*100:03.0f}'

    # LOAD DATA INTO DATAFRAME
    records = []
    for statsfile in filter(lambda x: x.suffix=='.stats',resultdir.iterdir()):
        print(f'Loading "{statsfile.stem}"')
        # stats[statsfile.stem] = sc.loadobj(statsfile)
        stats = sc.loadobj(statsfile)
        for d in stats:
            d['package'] = statsfile.stem
        records += stats
    df = pd.DataFrame.from_records(records)

    packages = df.loc[~df['package'].str.startswith('p_'),:]

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
    fig.savefig(resultdir / 'probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

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
    fig.savefig(resultdir / 'infection_size.png', bbox_inches='tight', dpi=300, transparent=False)

