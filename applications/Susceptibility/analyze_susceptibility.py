# Susceptibility distribution plots
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sciris as sc

resultsdir = Path(__file__).parent/'results'


stats = {}
for statsfile in filter(lambda x: x.suffix=='.stats',resultsdir.iterdir()):
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
fig.savefig(resultsdir / 'probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

# Boxplot of infection size
records = []
for scen_name in stats.index:
    vals = stats.at[scen_name,'cum_infections']
    for val in vals:
        records.append((scen_name, val))
df = pd.DataFrame.from_records(records, columns=['Scenario', 'Infections'], index='Scenario')

fig, ax = plt.subplots()
grouped = df.reset_index().groupby(['Scenario'])
df2 = pd.DataFrame({col:vals['Infections'] for col,vals in grouped})
means = df2.mean()
means.sort_values(ascending=True, inplace=True)
df2 = df2[means.index]
df2.boxplot()
fig.set_size_inches(16, 7)
fig.savefig(resultsdir / 'infection_size.png', bbox_inches='tight', dpi=300, transparent=False)


