# Plot susceptibility scenarios
import textwrap
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
import outbreak
import sciris as sc
import seaborn as sns

scendir = Path(__file__).parent/'scenarios'

# Load records in
records = []
for statsfile in scendir.rglob('*.stats'):
    stats = sc.loadobj(statsfile)
    for d in stats:
        d['scenario_name'] = statsfile.parent.name
        d['package_name'] = statsfile.stem
    records += stats
df = pd.DataFrame.from_records(records)

package_names = outbreak.load_packages('packages.csv')[1]
scenario_names = outbreak.load_scenarios('scenarios.csv')[1]
df['scenario_name'] = df['scenario_name'].replace(scenario_names)
df['package_name'] = df['package_name'].replace(package_names)
df['undiagnosed'] = df['cum_infections']-df['cum_diagnoses']
df.set_index(['scenario_name','package_name'],inplace=True)
scenarios = list(df.index.get_level_values(0).unique())
packages = list(df.index.get_level_values(1).unique())

# PERFORM BOOTSTRAP ANALYSIS
risk_levels = {50: '#ffbfbf', 100: '#ff8585', 250: '#c90000'}

level = 50
color = risk_levels[level]

def calc_prob(group, level, quantity, sample:bool=False):
    """
    Calculate probability of >level cumulative infections

    Args:
        group: Grouped dataset `df.reset_index().groupby(['scenario_name', 'package_name'])` where df is the results df
        level: Number of infections for threshold
        sample: If True, perform bootstrap resampling

    Returns: Dataframe with probability

    """
    if sample:
        n_samples = max(group[quantity].count())  # Number of simulation samples
        sampled_df = group.sample(n_samples,replace=True)
        group = sampled_df.reset_index().groupby(['scenario_name', 'package_name'])
    return group[quantity].agg(lambda x: sum(x > level)) / group[quantity].count()

def bootstrap_quantity(df, quantity, n_bootstrap=1000):
    group = df.reset_index().groupby(['scenario_name', 'package_name'])
    means = calc_prob(group,level, quantity)
    means.name = 'mean'
    mean_samples = [calc_prob(group,level,quantity, sample=True) for _ in range(n_bootstrap)]  # Bootstrap samples of the mean
    stds = pd.concat(mean_samples).groupby(['scenario_name', 'package_name']).std()
    stds.name = 'std'
    return pd.concat([means, stds], axis=1)

bootstrap_cum_infections = bootstrap_quantity(df, 'cum_infections')
bootstrap_undiagnosed = bootstrap_quantity(df, 'undiagnosed')

raise Exception('Manual stop')

### FIG 1 Boxplot

# grouped = df.loc[scenario_names['baseline']].groupby(['package_name'])
# df2 = pd.DataFrame({col:vals['cum_infections'].values for col,vals in grouped})
# means = df2.mean()
# means.sort_values(ascending=True, inplace=True)
# df2 = df2[means.index]
# fig, ax = plt.subplots()
# df2.boxplot()
# fig.set_size_inches(16, 7)
# plt.ylabel('Number of infections')
# plt.title('Number of infections after 30 days')
# plt.yscale('log')
# plt.savefig(scendir / f'fig3.png', bbox_inches='tight', dpi=300, transparent=False)
# plt.close()

fig, ax = plt.subplots()
sns.boxplot(order=list(package_names.values()),x='package_name',y='cum_infections',data=df.loc['Baseline'].reset_index())
plt.ylabel('Number of infections')
plt.title('Number of infections after 30 days')
plt.xlabel('')
plt.yscale('log')
fig.set_size_inches(14, 7)
plt.savefig(scendir / f'fig1a.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()
#
# fig, ax = plt.subplots()
# sns.boxplot(order=list(package_names.values()),x='package_name',y='peak_diagnoses',data=df.loc['Baseline'].reset_index())
# plt.ylabel('Number of diagnoses per day')
# plt.title('Maximum number of diagnoses per day (first 30 days of outbreak)')
# plt.xlabel('')
# plt.yscale('log')
# plt.savefig(scendir / f'fig1b.png', bbox_inches='tight', dpi=300, transparent=False)
# plt.close()
#
#
# fig, ax = plt.subplots()
# sns.boxplot(order=list(package_names.values()),x='package_name',y='undiagnosed',data=df.loc['Baseline'].reset_index())
# plt.ylabel('Number of cases')
# plt.title('Number of undiagnosed infections after 30 days')
# plt.xlabel('')
# plt.yscale('log')
# plt.savefig(scendir / f'fig1b.png', bbox_inches='tight', dpi=300, transparent=False)
# plt.close()


## FIG 2 BARS

px = bootstrap_cum_infections.loc['Baseline','mean']
sx = bootstrap_cum_infections.loc['Baseline','std']
order = px.argsort()
fig, ax = plt.subplots()
idx = np.arange(len(px))
plt.barh(idx,px.values[order], xerr=sx.values[order], color='#c90000',label=f'> {level}')
plt.yticks(idx, px.index[order])
plt.xlabel('Probability')
plt.title('Probability of outbreak >50 people')
plt.savefig(scendir / f'fig2.png', bbox_inches='tight', dpi=300, transparent=False)


px = bootstrap_undiagnosed.loc['Baseline','mean']
sx = bootstrap_undiagnosed.loc['Baseline','std']
order = px.argsort()
fig, ax = plt.subplots()
idx = np.arange(len(px))
plt.barh(idx,px.values[order], xerr=sx.values[order], color='#c90000',label=f'> {level}')
plt.yticks(idx, px.index[order])
plt.xlabel('Probability')
plt.title('Probability of >50 undiagnosed people')
plt.savefig(scendir / f'fig2.png', bbox_inches='tight', dpi=300, transparent=False)


## FIG 2a PROBABILITY CURVES

scenario = 'Baseline'
plt.figure()
for package in packages:
    outcomes = df.loc[(scenario, package),'cum_infections'].values
    sizes = 1+np.arange(500)
    probability = [sum(outcomes>i)/len(outcomes) for i in sizes]
    plt.plot(sizes,probability,label=package)
plt.legend()
plt.xlabel('Outbreak size (number of infections)')
plt.ylabel('Probability')
plt.savefig(scendir / f'fig1a.png', bbox_inches='tight', dpi=300, transparent=False)

scenario = 'Baseline'
plt.figure()
for package in packages:
    outcomes = df.loc[(scenario, package),'peak_diagnoses'].values
    sizes = 1+np.arange(100)
    probability = [sum(outcomes>i)/len(outcomes) for i in sizes]
    plt.plot(sizes,probability,label=package)
plt.legend()
plt.xlabel('Diagnoses per day')
plt.ylabel('Probability')
plt.savefig(scendir / f'fig1b.png', bbox_inches='tight', dpi=300, transparent=False)

# Plot infection size for each policy package across scenarios


# FIG 2 pcolor
level = 50
group = df.reset_index().groupby(['scenario_name','package_name'])
p = group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()
p = p.unstack()
p = p.sort_values(by='Baseline',axis=1)
fig, ax = plt.subplots()
plt.set_cmap('Reds')
c = ax.pcolor(p.to_numpy())
fig.colorbar(c, ax=ax)
ax.set_xticks(np.arange(len(p.columns))+0.5)
ax.set_xticklabels(p.columns,rotation=90)
ax.set_yticks(np.arange(len(scenarios))+0.5)
ax.set_yticklabels(scenarios)
for (i, j), z in np.ndenumerate(p.to_numpy()):
    if np.isfinite(z):
        ax.text(j+0.5, i+0.5, '{:0.2f}'.format(z), ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3',alpha=0.6,linewidth=0))
plt.title(f'Probability of more than {level} infections')
fig.savefig(scendir / f'fig2.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()

level = 20
group = df.reset_index().groupby(['scenario_name','package_name'])
p = group['peak_diagnoses'].agg(lambda x: sum(x > level)) / group['peak_diagnoses'].count()
p = p.unstack()
p = p.sort_values(by='Baseline',axis=1)
fig, ax = plt.subplots()
plt.set_cmap('Reds')
c = ax.pcolor(p.to_numpy())
fig.colorbar(c, ax=ax)
ax.set_xticks(np.arange(len(packages))+0.5)
ax.set_xticklabels(packages,rotation=90)
ax.set_yticks(np.arange(len(scenarios))+0.5)
ax.set_yticklabels(scenarios)
for (i, j), z in np.ndenumerate(p.to_numpy()):
    if np.isfinite(z):
        ax.text(j+0.5, i+0.5, '{:0.2f}'.format(z), ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3',alpha=0.6,linewidth=0))
plt.title(f'Probability of more than {level} diagnoses per day')
fig.savefig(scendir / f'fig2a.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()


# Proportion diagnosed
p =  df['undiagnosed']/df['cum_infections']
p = p.reset_index().groupby(['scenario_name', 'package_name']).mean()
p = p.unstack()
p.columns = p.columns.droplevel()
p = p[package_names.values()]
f, ax = plt.subplots(figsize=(9, 6))
sns.heatmap(p, annot=True, linewidths=.5, ax=ax, cmap='Reds')
plt.title('Proportion undiagnosed')

## R_eff
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
for (i, j), z in np.ndenumerate(p.to_numpy()):
    if np.isfinite(z):
        ax.text(j+0.5, i+0.5, '{:0.1f}'.format(z), ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3',alpha=0.9,linewidth=0))
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
for (i, j), z in np.ndenumerate(p.to_numpy()):
    if np.isfinite(z):
        ax.text(j+0.5, i+0.5, '{:0.1f}'.format(z), ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3',alpha=0.9,linewidth=0))
plt.title(f'Probability R_eff in last 7 days is > 1')
fig.savefig(scendir / f'reff_probability.png', bbox_inches='tight', dpi=300, transparent=False)
plt.close()


# Risk sensitivity analysis
level = 50
group = df.reset_index().groupby(['scenario_name', 'package_name'])
p = group['cum_infections'].agg(lambda x: sum(x > level)) / group['cum_infections'].count()
# p = group['r_eff7'].agg(lambda x: sum(x>1)) / group['cum_infections'].count()

for package in full_packages:

    fig, ax = plt.subplots()
    for i, scen in enumerate(scenarios):
        base_prob = p.loc['Baseline',package]
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
    plt.title(package)
    # plt.xlabel(f'% change in probability of R7<1')
    plt.xlim(-50,50)
    fig.savefig(scendir / f'scenario_comparison_{package}.png', bbox_inches='tight', dpi=300, transparent=False)
    plt.close()





## SIGNIFICANCE TESTING FOR DIFFERENT SCENARIOS
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
