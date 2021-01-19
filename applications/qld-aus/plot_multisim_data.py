#!/usr/bin/env python
# coding: utf-8
"""
Plot results from multisim objects
=======================================================


# author: Paula Sanz-Leon, QIMRB, January 2021
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
import covasim.misc as cvm
import sciris as sc
# Other goodies
import datetime # current date and time
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d_%H-%M-%S")


def get_simulated_data(key, sims):
    
    ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)

    # Moving average over 7 days
    for idx in range(yarr.shape[0]):
        yarr[idx, :] = np.convolve(yarr[idx, :], np.ones((3, ))/3, mode='same')

    return yarr
    



# Input data
inputs_folder = 'inputs'
input_data = 'qld_health_epi_data.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

# Set date as index
data.set_index('date', inplace=True)

# Start graphics objects
f, ax1 = plt.subplots(1, 1, figsize=(28, 18), sharex=True)

# Plot new cases
#import pdb; pdb.set_trace()
epi_data =  data['new_locally_acquired_cases'][0:68]
epi_data = np.convolve(epi_data, np.ones((3, ))/3, mode='same')
ax1.plot(data.index[0:68],epi_data, color='#e41a1c', ls='--')
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax1.set_xlim([datetime.date(2020, 1, 22), datetime.date(2020, 3, 30)])
ax1.set_ylabel('new cases')
plt.setp(ax1.get_xticklabels(), 
         rotation=45, ha="right",
         rotation_mode="anchor")


# Load multisim

# Filepaths
resultsfolder = 'results_recalibration_2020-01-15__2020-03-30'

# List of files to plot
list_of_files = ['qld_update_locally_acquired_recalibration_2020-01-15_2020-03-30_0.0110_08.obj']

msim = sc.loadobj(f'{resultsfolder}/{list_of_files[0]}')
sims = msim.sims
sim_data = get_simulated_data('new_infectious', sims)[:, cvm.day('2020-01-22', start_day='2020-01-15'):cvm.day('2020-03-30', start_day='2020-01-15')].T
#import pdb; pdb.set_trace()

ax1.plot(data.index[0:68], np.percentile(sim_data, 50, axis=1), color='black', alpha=0.5)

   
plt.show()


# Output data
#figs_folder = 'figs'
#output_fig =  "-".join((now_str, 'qld_health_epi_data_sims_dat.jpeg'))

#cv.savefig("/".join((figs_folder, output_fig)), dpi=100)
