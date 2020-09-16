from pathlib import Path
import pandas as pd
import covasim_australia as cva
import covasim.misc as cvm
import functools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

early_release = '2020-09-14'
late_release = '2020-09-28'

early = []
resultsdir = Path(__file__).parent/'projection_results'
for result in (resultsdir/early_release).rglob('projection*.csv'):
    df = pd.read_csv(result)
    df.set_index('t',inplace=True)
    early.append(df)

late = []
resultsdir = Path(__file__).parent/'projection_results'
for result in (resultsdir/late_release).rglob('projection*.csv'):
    df = pd.read_csv(result)
    df.set_index('t',inplace=True)
    late.append(df)


start_date = df['date'][0] # NOTE - all sims must have the same start date
end_date = df['date'].values[-1]

to_day = functools.partial(cvm.day, start_day=start_date)
to_date = functools.partial(cvm.date, start_date=start_date)




def common_format(ax):
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: to_date(x)))
    ax.locator_params('x', nbins=5, prune='both')
    # ax.set_xlim(0,to_day(end_date))
    plt.setp(ax.get_xticklabels(), ha="right", rotation=30)
    ax.axvline(x=to_day('2020-07-09'), color='grey', linestyle='--')
    ax.axvline(x=to_day('2020-07-23'), color='grey', linestyle='--')
    ax.axvline(x=to_day('2020-08-06'), color='grey', linestyle='--')
    ax.axvline(x=to_day(early_release), color='r', linestyle='--')
    ax.axvline(x=to_day(late_release), color='b', linestyle='--')

fig, ax = plt.subplots()
cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
cases = cases.copy()
cases.index = cases['Date'].map(to_day)
cases.sort_index(inplace=True)
cases = cases.loc[cases.index >= 0]['vic'].astype(int).cumsum()
ax.scatter(cases.index, cases.values, s=10, color='k', alpha=1.0)
ax.plot(cases.index, cases.values*1.1, linestyle='dashed', color='k', alpha=1.0)
ax.plot(cases.index, cases.values*0.9, linestyle='dashed', color='k', alpha=1.0)
for result in early:
    ax.plot(result.index, result['cum_diagnoses'], color='r', alpha=0.1)
for result in late:
    ax.plot(result.index, result['cum_diagnoses'], color='b', alpha=0.1)
ax.set_title('Cumulative diagnosed cases')
common_format(ax)


fig, ax = plt.subplots()
for result in early:
    ax.plot(result.index, result['new_diagnoses'], color='r', alpha=0.1)
for result in late:
    ax.plot(result.index, result['new_diagnoses'], color='b', alpha=0.1)
ax.set_title('New diagnoses')
cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')
cases['day'] = cases['Date'].map(to_day)
cases.set_index('day', inplace=True)
cases = cases.loc[cases.index >= 0]['vic'].astype(int)
ax.scatter(cases.index, cases.values, color='k', s=10, alpha=1.0)
common_format(ax)
ax.set_ylabel('Number of cases')


# Pick a day e.g 4 weeks after release
# Probability of having > XX cases/day
t_early = to_day(early_release)
t_late = to_day(late_release)
t_ref_early = to_day(early_release) + 28
t_ref_late = to_day(late_release) + 28
outbreak_threshold = 50 # cases/day

early_outbreak = 0
for df in early:
    if df.loc[t_ref_early - 6:t_ref_early, 'new_diagnoses'].mean() > outbreak_threshold:
        early_outbreak += 1
early_probability = early_outbreak/len(early)

late_outbreak = 0
for df in late:
    if df.loc[t_ref_late - 6:t_ref_late, 'new_diagnoses'].mean() > outbreak_threshold:
        late_outbreak += 1
late_probability = late_outbreak/len(late)


# early_release_diagnoses = [df.loc[to_day(early_release)]['new_diagnoses'] for df in early]
# late_release_diagnoses = [df.loc[to_day(late_release)]['new_diagnoses'] for df in late]

# What were the average number of cases when released?
t_early = to_day(early_release)
t_late = to_day(late_release)
t_ref_early = to_day(early_release) + 28
t_ref_late = to_day(late_release) + 28

x = []
for df in early:
    d = {}
    d['release_day'] = df.loc[t_early - 6:t_early, 'new_diagnoses'].mean()
    d['later'] = df.loc[t_ref_early - 6:t_ref_early, 'new_diagnoses'].mean()
    x.append(d)
early_size = pd.DataFrame.from_dict(x)

x = []
for df in late:
    d = {}
    d['release_day'] = df.loc[t_late - 6:t_late, 'new_diagnoses'].mean()
    d['later'] = df.loc[t_ref_late - 6:t_ref_late, 'new_diagnoses'].mean()
    x.append(d)
late_size = pd.DataFrame.from_dict(x)


fig, ax = plt.subplots()
plt.scatter(early_size['release_day'],early_size['later'],s=10, c='r')
plt.scatter(late_size['release_day'],late_size['later'],s=10, c='b')
plt.xlabel('New diagnoses/day at time of release (7 day average)')
plt.ylabel('New diagnoses/day 4 weeks later (7 day average)')