# Susceptibility distribution plots
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import textwrap
from pathlib import Path
import sciris as sc
import pandas as pd

# packages = pd.read_excel(rootdir / 'policy_packages.xlsx', index_col=0)
# packages = packages.T
# packages = packages.to_dict(orient='index')
# packages = {name: [policy for policy, active in package.items() if not pd.isnull(active)] for name, package in packages.items()}

rootdir = Path(__file__).parent


stats = {}
for statsfile in filter(lambda x: x.suffix=='.stats',rootdir.iterdir()):
    print(f'Loading "{statsfile.stem}"')
    stats[statsfile.stem] = sc.loadobj(statsfile)

stats = pd.DataFrame(stats).T

p_less_than_50 = []
p_less_than_100 = []
labels = []

for scen_name in stats.index:
    vals = np.array(stats.at[scen_name,'cum_infections'])
    p_less_than_50.append(sum(vals < 50) / len(vals))
    p_less_than_100.append(sum(vals < 100) / len(vals))


idx = np.argsort(p_less_than_100)[::-1]
p_gt_50 = 1 - np.array(p_less_than_50)
p_gt_100 = 1 - np.array(p_less_than_100)
ind = np.arange(len(idx))  # the x locations for the groups
width = 0.5  # the width of the bars: can also be len(x) sequence
plt.style.use('default')
fig, ax = plt.subplots()
p1 = plt.bar(ind, p_gt_50[idx] - p_gt_100[idx], width, bottom=p_gt_100[idx], label='> 50', color='b')
p2 = plt.bar(ind, p_gt_100[idx], width, label='> 100', color='r')
plt.ylabel('Probability')
plt.title('Probability of outbreak size')
wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(), 20)) for x in stats.index])
plt.xticks(ind, wrapped_labels[idx], rotation=0)
plt.legend()
plt.show()
fig.set_size_inches(16, 7)
# fig.savefig(rootdir / 'probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

# Boxplot of infection size
records = []
for scen_name in stats.index:
    vals = stats.at[scen_name,'cum_infections']
    for val in vals:
        records.append((scen_name, val))
df = pd.DataFrame.from_records(records, columns=['Scenario', 'Infections'], index='Scenario')

data = []
for scen in stats.index:
    data.append(df.loc[scen, 'Infections'].values)
fig, ax = plt.subplots()
ax.boxplot(data, showfliers=False)
wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(), 20)) for x in stats.index])

plt.xticks(1 + np.arange(len(stats.index)), wrapped_labels)
plt.title('Infection size after 30 days')
fig.set_size_inches(16, 7)
# fig.savefig(rootdir / 'infection_size.png', bbox_inches='tight', dpi=300, transparent=False)


if False:
    scenarios = {}
    for simfile in filter(lambda x: x.suffix=='.sims',rootdir.iterdir()):
        print(f'Loading "{simfile.stem}"')
        scenarios[simfile.stem] = sc.loadobj(simfile)

    p_less_than_50 = []
    p_less_than_100 = []
    labels = []

    for scen_name, sims in scenarios.items():
        vals = np.array([x.results['cum_infections'][-1] for x in sims])
        p_less_than_50.append(sum(vals < 50) / len(vals))
        p_less_than_100.append(sum(vals < 100) / len(vals))

    idx = np.argsort(p_less_than_100)[::-1]
    p_gt_50 = 1 - np.array(p_less_than_50)
    p_gt_100 = 1 - np.array(p_less_than_100)
    ind = np.arange(len(idx))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    plt.style.use('default')
    fig, ax = plt.subplots()
    p1 = plt.bar(ind, p_gt_50[idx] - p_gt_100[idx], width, bottom=p_gt_100[idx], label='> 50', color='b')
    p2 = plt.bar(ind, p_gt_100[idx], width, label='> 100', color='r')
    plt.ylabel('Probability')
    plt.title('Probability of outbreak size')
    wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(), 20)) for x in scenarios.keys()])
    plt.xticks(ind, wrapped_labels[idx], rotation=0)
    plt.legend()
    plt.show()
    fig.set_size_inches(16, 7)
    fig.savefig(rootdir/'probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

    # Boxplot of infection size
    records = []
    for scen_name, sims in scenarios.items():
        for sim in sims:
            infections = sim.results['cum_infections'][-1]
            doubling_time = sim.results['doubling_time'][-21:-7].mean()
            records.append((scen_name, infections, doubling_time))
    df = pd.DataFrame.from_records(records, columns=['Scenario', 'Infections', 'Doubling time'], index='Scenario')

    data = []
    for scen in scenarios.keys():
        data.append(df.loc[scen, 'Infections'].values)
    fig, ax = plt.subplots()
    ax.boxplot(data, showfliers=False)
    wrapped_labels = np.array(['\n'.join(textwrap.wrap(x.capitalize(), 20)) for x in scenarios.keys()])

    plt.xticks(1 + np.arange(len(scenarios)), wrapped_labels)
    plt.title('Infection size after 30 days')
    fig.set_size_inches(16, 7)
    fig.savefig(rootdir/'infection_size.png', bbox_inches='tight', dpi=300, transparent=False)