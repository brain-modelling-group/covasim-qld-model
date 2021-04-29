#!/usr/bin/env python
# coding: utf-8
"""
Plot gantt chart with the roadmap of QLD restrictions
=============================================================

# author: For QLD Paula Sanz-Leon, QIMRB, January 2021
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
import datetime # current date and time

import covasim.misc as cvm

# 
start_date = '2020-03-15'
end_date = '2020-05-31'
duration_length = cvm.day(end_date, start_day=start_date)

# Load empirical data
inputs_folder = 'inputs'
input_data = 'qld_policies.csv'

# Load data
policy_data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['start_date'])
fig, ax = plt.subplots()
ax1 = ax.twiny()

yticks = []
yticklabels = []
for idx in range(35):
    policy_start = policy_data["start_date"][idx]
    policy_end = policy_data["end_date"][idx]
    policy_length = cvm.day(policy_end, start_day=start_date) - cvm.day(policy_start, start_day=start_date)
    ax.broken_barh([(cvm.day(policy_start, start_day=start_date), policy_length)], (3*idx, 2), facecolors=policy_data["colour_level"][idx])
    yticks.append(3*idx)
    yticklabels.append(policy_data["intervention_brief_description"][idx]) 

ax.set_ylim(0, 110)
ax.set_xlim(0, duration_length-1)
ax.set_xlabel('days since Mar 15 2020')
ax.set_yticks(yticks)
import pdb; pdb.set_trace
ax.set_yticklabels(yticklabels)
ax.grid(True)

#ax1.set_xlim(ax.get_xlim())
ax1.set_xlim([datetime.date(2020, 3, 15), datetime.date(2020, 5, 31)])
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=MO, interval=1))
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
plt.setp(ax1.get_xticklabels(), rotation=30, ha="left", rotation_mode="anchor")

#import pdb; pdb.set_trace()
plt.tight_layout()
plt.show()


