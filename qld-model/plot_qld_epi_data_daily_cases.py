#!/usr/bin/env python
# coding: utf-8
"""
Plot QLD epidata taken from covidlive, covidata and ABS 
Plots new cases
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

source_keys = ['new_cases_source_overseas',
               'new_cases_source_interstate', 
               'new_cases_source_community', 
               'new_cases_source_unknown', 
               'new_cases_source_under_investigation']

# Output data
figs_folder = 'figs'
output_fig =  "-".join((now_str, 'qld_epi_data_daily_cases.jpeg'))

# import ipdb
# ipdb.set_trace()

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

# Set date as index
data.set_index('date', inplace=True)

# Start graphics objects
f, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(28, 18), sharex=True)


# Plot new cases
ax1.bar(data.index, data['new_cases'], width=0.9)
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.set_ylabel('new cases')
plt.setp(ax1.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")


# Plot new deaths
ax2.bar(data.index, data[source_keys[2]], color='#ad150b')
ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax2.set_ylabel('new cases \n(community transmission)')
plt.setp(ax2.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

# Plot imported cases
ax3.bar(data.index, data[source_keys[0]])
ax3.bar(data.index, data[source_keys[1]])
ax3.bar(data.index, data[source_keys[3]])
ax3.bar(data.index, data[source_keys[4]])
ax3.bar(data.index, data[source_keys[2]])
ax3.xaxis.set_major_locator(mdates.WeekdayLocator())
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax3.set_ylabel('new cases (other sources)')
plt.setp(ax3.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

# Plot new testing
ax4.bar(data.index, data['new_tests'], color='#e5a810')
ax4.xaxis.set_major_locator(mdates.WeekdayLocator())
ax4.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax4.set_ylabel('new tests')
plt.setp(ax4.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

cv.savefig("/".join((figs_folder, output_fig)), dpi=100)
