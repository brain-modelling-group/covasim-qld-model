#!/usr/bin/env python
# coding: utf-8
"""
Plot QLD epidata taken from covidlive, covidata and ABS 
Plots cumulative cases
=======================================================


# author: Paula Sanz-Leon, QIMRB, August 2020
#         
"""

# Import sciencey libraries
import pandas as pd
import numpy as np
# Import graphics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
sns.set(style="white", context="talk")
#rs = np.random.RandomState(8)
# Import covasim's goodies
import covasim as cv
# Other goodies
from datetime import datetime
# current date and time
now = datetime.now()
now_str = now.strftime("%Y-%m-%d_%H-%M-%S")


# Input data
inputs_folder = 'inputs'
input_data = 'qld_epi_data_wave_01_basic_stats.csv'

# Output data
figs_folder = 'figs'
output_fig =  "-".join((now_str, 'qld_epi_data_cumulative_cases.png'))

# import ipdb
# ipdb.set_trace()

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

# Set date as index
data.set_index('date', inplace=True)

# Start graphics objects
f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(18, 10), sharex=True)


# Plot new cases
ax1.bar(data.index, data['total_cases'])
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.set_ylabel('total cases')
plt.setp(ax1.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")


# Plot new deaths
ax2.bar(data.index, data['total_deaths'], color='#ad150b')
ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax2.set_ylabel('total deaths')
plt.setp(ax2.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

# Plot new testing
ax3.bar(data.index, data['total_tests'], color='#e5a810')
ax3.xaxis.set_major_locator(mdates.WeekdayLocator())
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax3.set_ylabel('total tests')
plt.setp(ax3.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

cv.savefig("/".join((figs_folder, output_fig)), dpi=100)
