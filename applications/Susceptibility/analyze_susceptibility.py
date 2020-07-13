# Susceptibility distribution plots
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import textwrap


def positive_kde(vals, npts=100):
    value_range = (vals.min(), vals.max())
    kernel = stats.gaussian_kde(np.concatenate([vals.ravel(), -vals.ravel()]))
    x = np.linspace(*value_range, npts)
    y = 2 * kernel(x)
    return x, y


del scenarios['Full relaxation']

p_less_than_50 = []
p_less_than_100 = []
labels = []

for scen_name in scenarios.keys():
    vals = np.array([x.results['cum_infections'][-1] for x in sims[scen_name]])
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
fig.savefig('probability_bars.png', bbox_inches='tight', dpi=300, transparent=False)

# Boxplot of infection size
records = []
for scen_name in scenarios.keys():
    for sim in sims[scen_name]:
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
fig.savefig('infection_size.png', bbox_inches='tight', dpi=300, transparent=False)