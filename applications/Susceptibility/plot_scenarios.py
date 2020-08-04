# Plot susceptibility scenarios
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

scendir = Path(__file__).parent/'scenarios'

df = pd.read_csv(scendir/'results.csv')
df.set_index(['scenario_name','package_name'],inplace=True)
scenarios = list(df.index.get_level_values(0).unique())
packages = list(df.index.get_level_values(1).unique())
risk_levels = {50: '#ffbfbf', 100: '#ff8585', 250: '#c90000'}

# Plot bar graph of infection size per scenario
for scenario in scenarios:

    df1 = df.loc[scenario]
    fig, ax = plt.subplots()
    order = None
    for n, color in risk_levels.items():
        p = df1.groupby('package_name')['cum_infections'].agg(lambda x: sum(x > n)) / df1.groupby('package_name')['cum_infections'].count()
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
    fig.savefig(scendir / f'probability_bars_{scenario}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()

# Plot infection size for each policy package across scenarios
for package in packages:
    df1 = df.xs(package, level=1)

    fig, ax = plt.subplots()
    grouped = df1.reset_index().groupby(['scenario_name'])
    df2 = pd.DataFrame({col:vals['cum_infections'] for col,vals in grouped})
    means = df2.mean()
    means.sort_values(ascending=True, inplace=True)
    df2 = df2[means.index]
    df2.boxplot()
    fig.set_size_inches(16, 7)
    plt.ylabel('Total number of infections')
    fig.savefig(scendir / f'infection_size_boxplot_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()


# Get a grid for a given infection size probability at a risk level
for level in risk_levels:
    group = df.reset_index().groupby(['scenario_name','package_name'])
    p = group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()
    p = p.unstack()

    fig, ax = plt.subplots()
    plt.set_cmap('Reds')
    c = ax.pcolor(p.to_numpy())
    fig.colorbar(c, ax=ax)

    ax.set_xticks(np.arange(len(packages))+0.5)
    ax.set_xticklabels(packages,rotation=90)
    ax.set_yticks(np.arange(len(scenarios))+0.5)
    ax.set_yticklabels(scenarios)
    plt.title(f'Probability of more than {level} infections')

    fig.savefig(scendir / f'risk_comparison_{level}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()

# R_eff
group = df.reset_index().groupby(['scenario_name','package_name'])
p = group['r_eff7'].mean()
p = p.unstack()
fig, ax = plt.subplots()
plt.set_cmap('Reds')
c = ax.pcolor(p.to_numpy())
fig.colorbar(c, ax=ax)
ax.set_xticks(np.arange(len(packages))+0.5)
ax.set_xticklabels(packages,rotation=90)
ax.set_yticks(np.arange(len(scenarios))+0.5)
ax.set_yticklabels(scenarios)
plt.title(f'R_eff over last 7 days')
fig.savefig(scendir / f'reff.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()

# Risk sensitivity analysis
sensitivity_rows = {
 'Test delay +/- 1 day':['slower_results','faster_results'],
 'Swab delay +/- 1 day':['slower_swabs','faster_swabs'],
 'Test proportion +/- 5%':['less_testing','more_testing'],
 'Isolation not required (+testing)':['more_testing_without_iso'],
 'Isolation not required (++testing)': ['even_more_testing_without_iso'],
'Test all quarantined': ['test_all_quarantined'],
}


level = 100
group = df.reset_index().groupby(['scenario_name', 'package_name'])
p = group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()

for package in packages:
    fig, ax = plt.subplots()
    for i, (row_name, scens) in enumerate(sensitivity_rows.items()):
        base = p.loc['baseline',package]
        worse = p.loc[scens[0],package] # outbreak probability should be *higher*
        width = max(0,(worse-base)/base*100)
        plt.barh(y=i, width=width,color='r')#, x=-width)

        if len(scens) > 1:
            better = p.loc[scens[1], package]  # outbreak probability should be *higher*
            width = max(0, (base - better) / base * 100)
            plt.barh(y=i, width=-width, color='b')  # , x=-width)

    plt.yticks(np.arange(len(sensitivity_rows)))
    ax.set_yticklabels(sensitivity_rows.keys())
    plt.xlabel(f'% change in probability of > {level} infections')
    plt.xlim(-50,50)
    fig.savefig(scendir / f'tornado_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()



# Yield - not interesting to look at because we aren't testing
y = df['cum_diagnoses']/df['cum_tests']
y.reset_index().groupby(['scenario_name', 'package_name']).mean()

for package in packages:
    df1 = df.xs(package, level=1)

    fig, ax = plt.subplots()
    grouped = df1.reset_index().groupby(['scenario_name'])
    df2 = pd.DataFrame({col:vals['cum_infections'] for col,vals in grouped})
    means = df2.mean()
    means.sort_values(ascending=True, inplace=True)
    df2 = df2[means.index]
    df2.boxplot()
    fig.set_size_inches(16, 7)
    plt.ylabel('Total number of infections')
    # fig.savefig(scendir / f'infection_size_boxplot_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    # plt.close()

