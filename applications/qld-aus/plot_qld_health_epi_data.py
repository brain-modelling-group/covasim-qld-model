#!/usr/bin/env python
# coding: utf-8
"""
Plot epidata from QLD heatlh
=======================================================


# author: Paula Sanz-Leon, QIMRB, December 2020
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
import datetime # current date and time
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d_%H-%M-%S")


# Input data
inputs_folder = 'inputs'
input_data = 'qld_health_epi_data.csv'



# Output data
figs_folder = 'figs'
output_fig =  "-".join((now_str, 'qld_health_epi_data.jpeg'))


# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

# Set date as index
#data.set_index('date', inplace=True)

# Start graphics objects
f, (ax1, ax2) = plt.subplots(2, 1, figsize=(28, 18), sharex=True)


# Plot new cases
new_cases = np.array(data['new_cases'])
ax1.plot(np.flip(new_cases))
# Set ticks every week
#ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
# Set major ticks format
#ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.set_ylabel('new cases')
plt.setp(ax1.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")

#import pdb
#pdb.set_trace()
# Plot new deaths
new_tests = np.array(data['new_tests'])
ax2.plot(np.flip(new_tests), color='#ad150b')
#ax2.xaxis.set_major_locator(mdates.WeekdayLocator())
#ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
#ax2.set_xlim([datetime.date(2020, 1, 22), datetime.date(2020, 12, 6)])
ax2.set_ylabel('new tests')
plt.setp(ax2.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")
   

cv.savefig("/".join((figs_folder, output_fig)), dpi=100)
