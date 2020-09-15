from pathlib import Path
import pandas as pd
import covasim_australia as cva
import covasim.misc as cvm
import functools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

resultsdir = Path(__file__).parent/'calibration_results'
results = {}
for result in resultsdir.rglob('calibration_*.csv'):
    df = pd.read_csv(result)
    seed = int(result.stem.split('_')[-1])
    results[seed] = df

summary = pd.read_csv(resultsdir/'summary.csv', index_col='seed')

start_date = df['date'][0] # NOTE - all sims must have the same start date
assert all([x['date'][0] == start_date for x in results.values()])
end_date = df['date'].values[-1]

to_day = functools.partial(cvm.day, start_day=start_date)
to_date = functools.partial(cvm.date, start_date=start_date)


cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
cases = cases.copy()
cases.index = cases['Date'].map(to_day)
cases.sort_index(inplace=True)

# Recompute accepted
# for seed, result in results.items():
#     # Get the last data day relative to the sim
#     data = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
#     data_end_t = data.index[-1]
#     data_end_value = data.values[-1]
#     model_end_value = result['cum_diagnoses'][data_end_t]
#     if abs(model_end_value - data_end_value) / data_end_value < 0.2:
#         summary.loc[seed, 'accepted'] = True
#     else:
#         summary.loc[seed, 'accepted'] = False



fig, ax = plt.subplots()
data = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
ax.scatter(data.index, data.values, s=10, color='k', alpha=1.0)
ax.plot(data.index, data.values*1.1, linestyle='dashed', color='k', alpha=1.0)
ax.plot(data.index, data.values*0.9, linestyle='dashed', color='k', alpha=1.0)


for seed, accepted in summary['accepted'].iteritems():
    if accepted:
        ax.plot(results[seed]['t'], results[seed]['cum_diagnoses'], color='r', alpha=0.4)
    else:
        ax.plot(results[seed]['t'], results[seed]['cum_diagnoses'], color='b', alpha=0.025)

    # ax.fill_between(s.base_sim.tvec, s.results['cum_diagnoses'].low, s.results['cum_diagnoses'].high, alpha=0.1)
    # ax.plot(s.base_sim.tvec, s.results['cum_diagnoses'].values[:], linestyle='dashed', color='b', alpha=0.1)

ax.set_title('Cumulative diagnosed cases')
# ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: to_date(x)))
ax.locator_params('x', nbins=5, prune='both')
# ax.set_xlim(0,to_day(end_date))
plt.setp(ax.get_xticklabels(), ha="right", rotation=30)
ax.axvline(x=to_day('2020-07-09'), color='grey', linestyle='--')
ax.axvline(x=to_day('2020-07-23'), color='grey', linestyle='--')
ax.axvline(x=to_day('2020-08-06'), color='grey', linestyle='--')

plt.figure()
plt.hist(summary['beta'])
plt.hist(summary.loc[summary.accepted]['beta'])