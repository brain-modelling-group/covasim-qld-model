from pathlib import Path
import pandas as pd
import covasim_australia as cva
import covasim.misc as cvm
import functools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import sciris as sc

resultsdir = Path(__file__).parent/'projection_results_v2_actual'

release_dates = [x.stem for x in resultsdir.iterdir()]

results = {}
for release_date in release_dates:
    results[release_date] = []
    for result in (resultsdir / release_date).rglob('projection*.csv'):
        df = pd.read_csv(result)
        df.set_index('t', inplace=True)
        results[release_date].append(df)

start_date = df['date'][0] # NOTE - all sims must have the same start date or else conversion to/from dates won't be correct for all sims
end_date = df['date'].values[-1] # NOTE - this assumes all sims have the same start date

to_day = functools.partial(cvm.day, start_day=start_date)
to_date = functools.partial(cvm.date, start_date=start_date)

colors = sc.gridcolors(len(release_dates))

def common_format(ax):
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: to_date(x)))
    ax.locator_params('x', nbins=5, prune='both')
    # ax.set_xlim(0,to_day(end_date))
    plt.setp(ax.get_xticklabels(), ha="right", rotation=30)
    ax.axvline(x=to_day('2020-07-09'), color='grey', linestyle='--')
    ax.axvline(x=to_day('2020-07-23'), color='grey', linestyle='--')
    ax.axvline(x=to_day('2020-08-06'), color='grey', linestyle='--')
    for date, color in zip(release_dates, colors):
        ax.axvline(x=to_day(date), color=color, linestyle='--')

# PLOT CUMULATIVE DIAGNOSES
fig, ax = plt.subplots()
cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
cases = cases.copy()
cases.index = cases['Date'].map(to_day)
cases.sort_index(inplace=True)
cases = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
ax.scatter(cases.index, cases.values, s=10, color='k', alpha=1.0)
ax.plot(cases.index, cases.values*1.1, linestyle='dashed', color='k', alpha=1.0)
ax.plot(cases.index, cases.values*0.9, linestyle='dashed', color='k', alpha=1.0)
for date, color in zip(release_dates, colors):
    for result in results[date]:
        ax.plot(result.index, result['cum_diagnoses'], color=color, alpha=0.1)
ax.set_title('Cumulative diagnosed cases')
common_format(ax)

# PLOT DAILY DIAGNOSES
fig, ax = plt.subplots()
for date, color in zip(release_dates, colors):
    for result in results[date]:
        ax.plot(result.index, result['new_diagnoses'], color=color, alpha=0.1)
ax.set_title('New diagnoses')
cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
cases['day'] = cases['Date'].map(to_day)
cases.set_index('day', inplace=True)
cases = cases.loc[cases.index >= 0]['vic'].astype(int)
ax.scatter(cases.index, cases.values, color='k', s=10, alpha=1.0)
common_format(ax)
ax.set_ylabel('Number of cases')

# SCATTER OUTBREAK SIZE VS INITIAL DIAGNOSIS RATE
fig, ax = plt.subplots()

for date, color in zip(release_dates, colors):
    t_release = to_day(date)
    t_ref = t_release + 28
    initial = [df.loc[t_release - 6:t_release, 'new_diagnoses'].mean() for df in results[date]]
    final = [df.loc[t_ref - 6:t_ref, 'new_diagnoses'].mean() for df in results[date]]
    plt.scatter(initial, final,s=10, color=color, label=date)

plt.xlabel('New diagnoses/day at time of release (7 day average)')
plt.ylabel('New diagnoses/day 4 weeks later (7 day average)')
plt.legend()

# OUTBREAK PROBABILITY
threshold = 100 # diagnoses/day
for date in release_dates:
    t_release = to_day(date)
    t_ref = t_release + 28
    final = np.array([df.loc[t_ref - 6:t_ref, 'new_diagnoses'].mean() for df in results[date]])
    print(f'{date}: {sum(final>threshold)/len(final)} probability of > {threshold} diagnoses/day after 4 weeks')

