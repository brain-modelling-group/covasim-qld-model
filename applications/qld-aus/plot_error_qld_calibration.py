#!/usr/bin/env python
# coding: utf-8
"""
Plot QLD results obtained with run_qld_wave_02.py with 
different calibration end dates 
=============================================================


# author: For QLD Paula Sanz-Leon, QIMRB, September 2020
"""

import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches
import matplotlib.pyplot as plt

# Filepaths
resultsfolder = 'results_recalibration'
figsfolder = 'figs'

list_of_files = ['qld_recalibration_2020-06-30_01.obj',
                 'qld_recalibration_2020-06-30_02.obj',
                 'qld_recalibration_2020-06-30_03.obj',
                 'qld_recalibration_2020-06-30_04.obj',
                 'qld_recalibration_2020-06-30_05.obj',
                 'qld_recalibration_2020-06-30_06.obj',
                 'qld_recalibration_2020-06-30_07.obj',
                 'qld_recalibration_2020-06-30_08.obj',
                 'qld_recalibration_2020-06-30_09.obj',
                 'qld_recalibration_2020-06-30_10.obj']

def format_ax(ax, sim, key=None):
    @ticker.FuncFormatter
    def date_formatter(x, pos):
        return (sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')
    ax.xaxis.set_major_formatter(date_formatter)
    if key != 'r_eff':
        sc.commaticks()
    pl.xlim([0, sim['n_days']])
    sc.boxoff()
    return


def get_data(key, sims, ax, calib=False, label='', ylabel='', low_q=25, high_q=75, flabel=True, start_day=None, subsample=2, choose_run=0):
    main_colour = [31/255.0, 120/255.0, 180/255.0]  
    
    ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)

     # Moving average over X-days
    num_days = 3
    for idx in range(yarr.shape[0]):
        yarr[idx, :] = np.convolve(yarr[idx, :], np.ones((num_days, ))/num_days, mode='same')

    if choose_run is not None:
        single_sim = sims[choose_run].results[key].values

    low  = np.percentile(yarr, low_q, axis=0)
    high = np.percentile(yarr, high_q, axis=0)
    halfsies = np.percentile(yarr, 50, axis=0)

    single_sim = sims[0] # For having a sim to refer to regarding time
    tvec = np.arange(len(low))

    
    start_day_idx = single_sim.day(start_day)
    
    end_day_idx = None
    
    return tvec, main_colour, halfsies


# Fonts and sizes
font_size = 20
pl.rcParams['font.size'] = font_size
pl.figure(figsize=(24,8))

# Plot locations
ygaps = 0.06
xgaps = 0.06
remainingy = 1-3*ygaps
remainingx = 1-3*xgaps
mainplotheight = 0.85
mainplotwidth = 0.85

@ticker.FuncFormatter
def date_formatter(x, pos):
    return (dt.date(2020, 2, 15) + dt.timedelta(days=x)).strftime('%b-%d')

# Plot diagnoses
x0, y0, dx, dy = xgaps, ygaps, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])

# Load the data
data_arr = np.zeros((len(list_of_files), 137))

for file_idx, this_file in enumerate(list_of_files):
    msim = sc.loadobj(f'{resultsfolder}/{this_file}')
    sims = msim.sims
    #format_ax(ax1, sims[0])
    tvec, color, data_arr[file_idx, ...] = get_data('new_diagnoses', sims, ax1, label='model data', ylabel='new diagnoses')

# Plot empirical data
inputs_folder = 'inputs'
input_data = 'qld_epi_data_wave_01_basic_stats.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])
start_idx = sims[0].day('2020-01-25')
end_idx = sims[0].day('2020-06-30')-start_idx
xx = data['new_cases'][-start_idx:end_idx]

num_days = 3
xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')
# error distribution between empirical data and median prediction
# [num par values, timepoints]
yy = np.abs(data_arr[:, 0:-1].T-xx[:, np.newaxis])
yy_med = np.percentile(yy, q=50, axis=0)
yy_q1  = np.percentile(yy, q=25, axis=0)
yy_q3  = np.percentile(yy, q=75, axis=0)

#import pdb; pdb.set_trace()
pl.errorbar(np.arange(len(list_of_files))+1, yy_med, np.array([yy_q1, yy_q3]), c='k', ecolor='r', marker='x', lw=2, alpha=1)

pl.legend(loc='upper right', frameon=False)
pl.ylabel('Q2 - abs(model-empirical)')
pl.xlabel('number of seed infections')
#ax1.set_ylim([0, 130])
plt.show()
