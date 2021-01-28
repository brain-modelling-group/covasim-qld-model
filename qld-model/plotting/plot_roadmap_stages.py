#!/usr/bin/env python
# coding: utf-8
"""
Plot gantt chart with the roadmap of QLD restrictions
=============================================================

# author: For QLD Paula Sanz-Leon, QIMRB, January 2021
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU
import datetime # current date and time

import covasim.misc as cvm

# 
start_date = '2020-03-16'

# Stage 0	Lockdown
stage_00_start = '2020-03-23'
stage_00_end   = '2020-05-01'
stage_00_length = cvm.day(stage_00_end, start_day=start_date) - cvm.day(stage_00_start, start_day=start_date)

# Stage 1	Easing
stage_01_start = '2020-05-01'
stage_01_end   = '2020-06-11'
stage_01_length = cvm.day(stage_01_end, start_day=start_date) - cvm.day(stage_01_start, start_day=start_date)

#Stage 2	Easing
stage_02_start = '2020-06-11'
stage_02_end   = '2020-07-02'
stage_02_length = cvm.day(stage_02_end, start_day=start_date) - cvm.day(stage_02_start, start_day=start_date)

# Stage 3	Easing
stage_03_start = '2020-07-02'
stage_03_end   = '2020-09-30'
stage_03_length = cvm.day(stage_03_end, start_day=start_date) - cvm.day(stage_03_start, start_day=start_date)

# Stage 4	Easing
stage_04_start = '2020-09-30'
stage_04_end   = '2020-11-02'
stage_04_length = cvm.day(stage_04_end, start_day=start_date) - cvm.day(stage_04_start, start_day=start_date)

# Stage 5	Easing
stage_05_start = '2020-11-02'
stage_05_end   = '2020-11-30'
stage_05_length = cvm.day(stage_05_end, start_day=start_date) - cvm.day(stage_05_start, start_day=start_date)

# Stage 6	Recovery
stage_06_start = '2020-11-30'
stage_06_end   = '2021-01-08'
stage_06_length = cvm.day(stage_06_end, start_day=start_date) - cvm.day(stage_06_start, start_day=start_date)

# Stage 000	Lockdown 2021
stage_000_start = '2021-01-08'
stage_000_end   = '2021-01-11'
stage_000_length = cvm.day(stage_000_end, start_day=start_date) - cvm.day(stage_000_start, start_day=start_date)

# Stage 001	- postlockdown 
stage_001_start = '2021-01-11'
stage_001_end   = '2021-01-21'
stage_001_length = cvm.day(stage_001_end, start_day=start_date) - cvm.day(stage_001_start, start_day=start_date)

fig, ax = plt.subplots()
ax1 = ax.twiny()
ax.broken_barh([(cvm.day(stage_00_start, start_day=start_date), stage_00_length)], (5, 5), facecolors='black')
ax.broken_barh([(cvm.day(stage_01_start, start_day=start_date), stage_01_length)], (10, 5), facecolors='#d73027')
ax.broken_barh([(cvm.day(stage_02_start, start_day=start_date), stage_02_length)], (15, 5), facecolors='#fc8d59')
ax.broken_barh([(cvm.day(stage_03_start, start_day=start_date), stage_03_length)], (20, 5), facecolors='#fee08b')
ax.broken_barh([(cvm.day(stage_04_start, start_day=start_date), stage_04_length)], (25, 5), facecolors='#d9ef8b')
ax.broken_barh([(cvm.day(stage_05_start, start_day=start_date), stage_05_length)], (30, 5), facecolors='#91cf60')
ax.broken_barh([(cvm.day(stage_06_start, start_day=start_date), stage_06_length)], (35, 5), facecolors='#1a9850')
ax.broken_barh([(cvm.day(stage_000_start, start_day=start_date), stage_000_length)], (40, 5), facecolors='black')
ax.broken_barh([(cvm.day(stage_001_start, start_day=start_date), stage_001_length)], (45, 5), facecolors='#d9ef8b')


ax.set_ylim(0, 50)
ax.set_xlim(0, 295+14)
ax.set_xlabel('days since lockdown')
ax.set_yticks([5, 10, 15, 20, 25, 30, 35, 40, 45])
ax.set_yticklabels(['Lockdown 20', 'stage 1', 'stage 2', 'stage 3', 'stage 4', 'stage 5', 'Recovery', 'Lockdown 21', 'Easing'])
ax.grid(True)

#ax1.set_xlim(ax.get_xlim())
ax1.set_xlim([datetime.date(2020, 3, 16), datetime.date(2021, 1, 21)])
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=MO, interval=2))
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
plt.setp(ax1.get_xticklabels(), rotation=30, ha="center", rotation_mode="anchor")

#import pdb; pdb.set_trace()
plt.show()


