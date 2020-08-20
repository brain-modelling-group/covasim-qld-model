# Plot susceptibility scenarios
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats

import sciris as sc

scendir = Path(__file__).parent/'scenarios'

df = pd.read_csv(scendir/'results.csv')
df.set_index(['scenario_name','package_name'],inplace=True)
scenarios = list(df.index.get_level_values(0).unique())
packages = list(df.index.get_level_values(1).unique())
risk_levels = {50: '#ffbfbf', 100: '#ff8585', 250: '#c90000'}

raise Exception('Manual stop')

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
plt.title(f'R_eff averaged over last 7 days')
fig.savefig(scendir / f'reff.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()

group = df.reset_index().groupby(['scenario_name','package_name'])
p = group['r_eff7'].agg(lambda x: sum(x>1)) / group['cum_infections'].count()
p = p.unstack()
fig, ax = plt.subplots()
plt.set_cmap('Reds')
c = ax.pcolor(p.to_numpy())
fig.colorbar(c, ax=ax)
ax.set_xticks(np.arange(len(packages))+0.5)
ax.set_xticklabels(packages,rotation=90)
ax.set_yticks(np.arange(len(scenarios))+0.5)
ax.set_yticklabels(scenarios)
plt.title(f'Probability R_eff in last 7 days is > 1')
fig.savefig(scendir / f'reff_probability.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()


# Risk sensitivity analysis
level = 50
group = df.reset_index().groupby(['scenario_name', 'package_name'])
p = group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()
# p = group['r_eff7'].agg(lambda x: sum(x>1)) / group['cum_infections'].count()

for package in packages:

    fig, ax = plt.subplots()
    for i, scen in enumerate(scenarios):
        base_prob = p.loc['baseline',package]
        scen_prob = p.loc[scen,package] # outbreak probability should be *higher*
        change = 100*(scen_prob-base_prob)/base_prob
        if change > 0: # It's worse
            color = 'r'
        else:
            color = 'b'

        plt.barh(y=i, width=change,color=color)#, x=-width)


    plt.yticks(np.arange(len(scenarios)))
    ax.set_yticklabels(scenarios)
    plt.xlabel(f'% change in probability of > {level} infections')
    # plt.xlabel(f'% change in probability of R7<1')
    plt.xlim(-50,50)
    fig.savefig(scendir / f'scenario_comparison_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()

# Plot outbreak size with error bars
level = 100
color = risk_levels[level]

group = df.reset_index().groupby(['scenario_name', 'package_name'])
n_bootstrap = 1000 # Number of bootstrap iterations for uncertainty

def calc_prob(group, level, sample:bool=False):
    """
    Calculate probability of >level cumulative infections

    Args:
        group: Grouped dataset `df.reset_index().groupby(['scenario_name', 'package_name'])` where df is the results df
        level: Number of infections for threshold
        sample: If True, perform bootstrap resampling

    Returns: Dataframe with probability

    """
    if sample:
        n_samples = max(group['cum_infections'].count())  # Number of simulation samples
        sampled_df = group.sample(n_samples,replace=True)
        group = sampled_df.reset_index().groupby(['scenario_name', 'package_name'])
    return group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()

means = calc_prob(group,level)
mean_samples = [calc_prob(group,level,True) for _ in range(n_bootstrap)]  # Bootstrap samples of the mean
stds = pd.concat(mean_samples).groupby(['scenario_name', 'package_name']).std().sort_index()

for package in packages:

    px = means.reorder_levels(['package_name', 'scenario_name']).loc[package]
    sx = stds.reorder_levels(['package_name', 'scenario_name']).loc[package]

    fig, ax = plt.subplots()

    idx = np.arange(len(px))
    plt.barh(idx,px.values, xerr=sx.values, color=color,label=f'> {level}')
    plt.legend()

    # Check significance
    labels = []
    for scenario in px.index.values:
        z = [x.loc[('baseline',package)] - x.loc[(scenario, package)] for x in mean_samples]
        null_hypothesis = np.percentile(z, 2.5) < 0 and np.percentile(z, 100 - 2.5) > 0
        significant = ~null_hypothesis
        if significant and scenario != 'baseline':
            labels.append('*'+scenario)
        else:
            labels.append(scenario)

    plt.yticks(idx, labels)


    plt.ylabel(None)
    plt.xlabel('Probability')
    ax.invert_yaxis()
    plt.title('Probability of outbreak size')
    fig.set_size_inches(16, 7)
    fig.savefig(scendir / f'probability_errorbars_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()


# For each package, is it significantly different to baseline?
# For each scenario, maybe ANOVA across packages?
significant_means = means.copy()
significant_means['significant'] = False
for package in packages:
    for scenario in scenarios:
        pass

        z = [x.loc[('baseline',package)] - x.loc[(scenario, package)] for x in mean_samples]
        null_hypothesis = np.percentile(z, 2.5) < 0 and np.percentile(z, 100 - 2.5) > 0

        res = scipy.stats.ttest_ind(mean_samples.loc[('baseline',package)].values,mean_samples.loc[('test_all_quarantined',package)].values,equal_var=False)

res = scipy.stats.ttest_ind(mean_samples.loc[('baseline',package)].values,mean_samples.loc[('test_all_quarantined',package)].values,equal_var=False)
