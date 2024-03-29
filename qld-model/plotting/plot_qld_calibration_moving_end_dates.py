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

list_of_files = [
                 'qld_update_locally_acquired_recalibration_2020-05-15_01.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_02.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_03.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_04.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_05.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_06.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_07.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_08.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_09.obj',
                 'qld_update_locally_acquired_recalibration_2020-05-15_10.obj'
                 ]

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


def plotter(key, sims, ax, calib=False, label='', ylabel='', low_q=0.01, high_q=0.99, flabel=True, start_day=None, subsample=2, choose_run=0):

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

    low  = pl.quantile(yarr, q=low_q, axis=0)
    high = pl.quantile(yarr, q=high_q, axis=0)
    halfsies = pl.quantile(yarr, q=0.5, axis=0)

    single_sim = sims[0] # For having a sim to refer to regarding time
    tvec = np.arange(len(low))

    if key in single_sim.data:
        data_t = np.array((single_sim.data.index-single_sim['start_day'])/np.timedelta64(1,'D'))
        inds = np.arange(0, len(data_t), subsample)
        pl.plot(data_t[inds], single_sim.data[key][inds], 'd', c=main_colour, markersize=10, alpha=0.2, label='data')

    
    start_day_idx = single_sim.day(start_day)
    
    end_day_idx = None
    
    
    pl.fill_between(tvec[start_day_idx:end_day_idx], 
                     low[start_day_idx:end_day_idx], 
                     high[start_day_idx:end_day_idx], facecolor=main_colour, alpha=0.3)

    pl.plot(tvec[start_day_idx:end_day_idx], 
            halfsies[start_day_idx:end_day_idx], c=main_colour, label=label, lw=2, alpha=0.7)
    #pl.bar(tvec[start_day_idx:end_day_idx], 
    #        halfsies[start_day_idx:end_day_idx], color=main_colour, label=label, alpha=0.4)
    
    
    sc.setylim()
    xmin, xmax = ax.get_xlim()
    pl.ylabel(ylabel)

    return tvec, main_colour, halfsies


def plot_intervs(sim, labels=True):

    color = [0, 0, 0]
    mar15 = sim.day('2020-03-15')
    mar19 = sim.day('2020-03-19')
    mar23 = sim.day('2020-03-23')
    apr04 = sim.day('2020-04-03')
    may01 = sim.day('2020-05-01')
    jul10 = sim.day('2020-07-10')
    aug05 = sim.day('2020-08-05')

    for day in [mar15, mar19, mar23, apr04, may01, jul10, aug05]:
        pl.axvline(day, c=color, linestyle='--', alpha=0.4, lw=3)

    if labels:
        yl = pl.ylim()
        labely = yl[1]*0.95
        pl.text(mar15, labely*1.15, 'Physical \ndistancing', bbox=dict(facecolor='#e5d210', alpha=0.5), color=color, alpha=0.9, style='italic')
        pl.text(mar19+1, labely, 'Outdoors \nrestricted',  bbox=dict(facecolor='#e5ae10', alpha=0.7), color=color, alpha=0.9, style='italic')
        pl.text(mar23+1, labely*0.92,  'Lockdown',  bbox=dict(facecolor='red', alpha=0.5), color=color, alpha=0.9, style='italic')
        pl.text(apr04+1, labely*0.7, 'QLD \nborder \nclosed', bbox=dict(facecolor='red', alpha=0.7), color=color, alpha=0.9, style='italic')
        pl.text(may01+1, labely, 'Begin phased \nrelease', color=color, alpha=0.9, style='italic')
        pl.text(jul10+1, labely, '\nQLD \nborder \nopen',  color=color, alpha=0.9, style='italic')
        pl.text(aug05+1, labely, '\nQLD \nborder \nclosed', color=color, alpha=0.9, style='italic')
    return

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
    return (dt.date(2020,2,15) + dt.timedelta(days=x)).strftime('%b-%d')

# Plot diagnoses
x0, y0, dx, dy = xgaps, ygaps, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])

#

# Load the data
halfsies_arr = np.zeros((len(list_of_files), 137))

for file_idx, this_file in enumerate(list_of_files):
    msim = sc.loadobj(f'{resultsfolder}/{this_file}')
    sims = msim.sims
    format_ax(ax1, sims[0])
    tvec, color, halfsies_arr[file_idx, :] = plotter('new_diagnoses', sims, ax1, label='model data', ylabel='new diagnoses')


# Plot empirical data
inputs_folder = 'inputs'
input_data = 'qld_epi_data_wave_01_basic_stats.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])
start_idx = sims[0].day('2020-01-25')
end_idx = sims[0].day('2020-06-30')-start_idx
xx = data['new_cases'][-start_idx:end_idx]
zz = data['new_cases_source_community'][-start_idx:end_idx]
tt = data['new_tests'][-start_idx:end_idx]

num_days = 3
xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')
zz = np.convolve(zz, np.ones((num_days, ))/num_days, mode='same')

#import pdb; pdb.set_trace()

#pl.bar(tvec[0:-(tvec.shape[0] - xx.shape[0])], xx, color='b', label='epi data', alpha=0.4)
pl.plot(tvec[0:-(tvec.shape[0] - xx.shape[0])], xx, c='b', marker='x', lw=2, label='empirical data (source: all)', alpha=1)
pl.plot(tvec[0:-(tvec.shape[0] - xx.shape[0])], zz, c='r', marker='o', lw=2, label='empirical data (source: community)', alpha=1)
pl.plot(tvec[0:-(tvec.shape[0] - xx.shape[0])], tt/1000.0, c='g', marker='o', lw=2, label='new tests', alpha=1)

pl.legend(loc='upper right', frameon=False)

ax1.set_ylim([0, 130])
plt.show()
