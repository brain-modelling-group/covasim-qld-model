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
resultsfolder = '/home/paula/Dropbox/COVID/simulated-data/resurgence/case-cloz'
figsfolder = resultsfolder
output_fig = 'new_cases_timeseries_cloz.png'

# list_of_files = ['qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.1000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.1500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.2000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.2500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.3000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.3500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.4000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.4500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.5000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.5500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.6000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.6500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.7000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.7500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.8000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.8500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.9000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_0.9500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.0500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.1000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.1500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.2000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.2500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.3000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.3500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.4000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.4500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.5000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.5500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.6000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.6500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.7000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.7500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.8000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.8500.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.9000.obj',
#                 'qld_distributed_2021-02-01_2021-03-31_iqf_0.3000_poisson_1.9500.obj']
#
list_of_files = ['qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0001.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0002.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0003.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0004.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0005.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0006.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0007.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0008.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0009.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0010.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0011.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0012.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0013.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0014.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0015.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0016.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0017.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0018.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0019.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0020.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0021.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0022.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0023.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0024.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0025.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0026.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0027.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0028.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0029.obj',
'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0030.obj']

                  
def format_ax(ax, sim, start_day_idx=0, key=None):
    @ticker.FuncFormatter
    def date_formatter(x, pos):
        return (sim['start_day'] + dt.timedelta(days=x)).strftime('%b-%d')
    ax.xaxis.set_major_formatter(date_formatter)
    if key != 'r_eff':
        sc.commaticks()
    pl.xlim([start_day_idx, sim['n_days']-7])
    #sc.boxoff()
    return


def plotter(key, sims, ax, label='', ylabel='', low_q=0.025, high_q=0.975, main_colour=[0.0, 0.0, 0.0], start_day=None, subsample=2, choose_run=0):
    
    ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)

    # Moving average over 7 days
    for idx in range(yarr.shape[0]):
         yarr[idx, :] = np.convolve(yarr[idx, :], np.ones((3, ))/3, mode='same')

    if choose_run is not None:
        single_sim = sims[choose_run].results[key].values

    low  = pl.quantile(yarr, q=low_q, axis=0)
    high = pl.quantile(yarr, q=high_q, axis=0)
    halfsies = pl.quantile(yarr, q=0.5, axis=0)

    single_sim = sims[0] # For having a sim to refer to regarding time
    tvec = np.arange(len(low))

    # if key in single_sim.data:
    #     data_t = np.array((single_sim.data.index-single_sim['start_day'])/np.timedelta64(1,'D'))
    #     inds = np.arange(0, len(data_t), subsample)
    #     pl.plot(data_t[inds], single_sim.data[key][inds], 'd', c=main_colour, markersize=10, alpha=0.1, label='data')

    
    start_day_idx = single_sim.day(start_day)
    start_day_fill = single_sim.day('2021-02-01')
    end_day_idx = -1
    
    
    #pl.fill_between(tvec[start_day_fill:end_day_idx], 
    #                low[start_day_fill:end_day_idx], 
    #                high[start_day_fill:end_day_idx], facecolor=main_colour, alpha=0.2)

    pl.plot(tvec[start_day_fill:end_day_idx], yarr[0:-1:50, start_day_fill:end_day_idx].T, c=main_colour, alpha=0.1)
    #pl.plot(tvec[start_day_idx:start_day_fill+1], yarr[:, start_day_idx:start_day_fill+1].T, c=[0.0, 0.0, 0.0], alpha=0.05)

    #pl.plot(tvec[start_day_idx:start_day_fill+1], halfsies[start_day_idx:start_day_fill+1], c=[0.0, 0.0, 0.0], alpha=0.7)
    pl.plot(tvec[start_day_fill:end_day_idx], halfsies[start_day_fill:end_day_idx], c=[0.5, 0.5, 0.5], label=label, lw=4, alpha=0.5)
    pl.plot(tvec[start_day_fill:end_day_idx], halfsies[start_day_fill:end_day_idx], c=main_colour, label=label, lw=2, alpha=1.0)

    # Resurgence limits
    pl.plot([tvec[start_day_idx], tvec[end_day_idx]], [5, 5], c=[1.0, 0.3945, 0.0], lw=1)
    #pl.plot([tvec[start_day_idx], tvec[end_day_idx]], [50, 50], c=[0.5, 0.0, 0.0], lw=1)
    #sc.setylim()
    xmin, xmax = ax.get_xlim()
    pl.ylabel(ylabel)


# Fonts and sizes
font_size = 16
pl.rcParams['font.size'] = font_size

@ticker.FuncFormatter
def date_formatter(x, pos):
    return (dt.date(2021,2,1) + dt.timedelta(days=x)).strftime('%b-%d')

# Plot diagnoses
this_fig, ax1 = plt.subplots(figsize=(9, 5))


#colours = ['#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026']
#colours = ['#006837', '#1a9850', '#66bd63', '#a6d96a', '#fdae61', '#f46d43', '#d73027', '#a50026']


import matplotlib.cm as cm
import matplotlib as mpl 

num_cases = len(list_of_files)
num_cases = num_cases//2 

cmap = cm.get_cmap('Spectral_r', num_cases+1)

norm_cbar = mpl.colors.Normalize(vmin=0,vmax=num_cases)     

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_cbar)
sm.set_array([])

start_display_day = '2021-02-01' 
# Load the data
for file_idx, this_file in enumerate(list_of_files):
    msim = sc.loadobj(f'{resultsfolder}/{this_file}')
    sims = msim.sims
    format_ax(ax1, sims[0], start_day_idx=sims[0].day(start_display_day))
    main_colour =  list(cmap(file_idx/len(list_of_files)))[0:-1]
    plotter('new_diagnoses', sims, ax1, label='model predictions', ylabel=r'new daily diagnoses', start_day=start_display_day, main_colour=main_colour)
#plt.yscale('log')
plt.ylim([0.0, 15])
plt.xlim([0, 42])


#plot_intervs(sims[0])
cbar = plt.colorbar(sm, ticks=np.linspace(0.5, num_cases-0.5, num_cases), 
                        boundaries=np.arange(0, num_cases+1, 1))

#cbar_labels = [f'{label:.2f}' for label in np.linspace(0.1, 1.95, num_cases)]
cbar_labels = [f'{np.round(label):.0f}' for label in np.linspace(1.0, 30.0, num_cases)]

cbar.ax.get_yaxis().labelpad = 55
cbar.ax.set_ylabel('average daily imported infections \nsince Feb 1st', rotation=270)
cbar.ax.set_yticklabels(cbar_labels)  # vertically oriented colorbar

import covasim as cv
cv.savefig("/".join((figsfolder, output_fig)), dpi=300)

plt.show()
