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

import seaborn as sns
sns.set_context("paper", font_scale=1.9)

# Filepaths
results_folder = '/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/case-cloz'
#results_folder = '/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/case-cluk'
#results_folder = '/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/case-clin'

figure_folder = 'fig-files'
figure_filename = 'new_infections_timeseries_cloz.png'
#figure_filename = 'new_infections_timeseries_cluk.png'
#figure_filename = 'new_infections_timeseries_clin.png'


# List of files to plot
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
                 'qld_cluster_2021-02-01_2021-03-31_iqf_0.3000_0015.obj']

                  
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

    if choose_run is not None:
        single_sim = sims[choose_run].results[key].values

    low  = pl.quantile(yarr, q=low_q, axis=0)
    high = pl.quantile(yarr, q=high_q, axis=0)
    halfsies = pl.quantile(yarr, q=0.5, axis=0)

    single_sim = sims[0] # For having a sim to refer to regarding time
    tvec = np.arange(len(low))
    
    start_day_idx = single_sim.day(start_day)
    start_day_fill = single_sim.day('2021-02-02')
    end_day_idx = -1
    

    pl.plot(tvec[start_day_fill:end_day_idx], yarr[0:-1:50, start_day_fill:end_day_idx].T, c=[0.5, 0.5, 0.5], alpha=0.05)
    #pl.plot(tvec[start_day_idx:start_day_fill+1], yarr[:, start_day_idx:start_day_fill+1].T, c=[0.0, 0.0, 0.0], alpha=0.05)

    #pl.plot(tvec[start_day_idx:start_day_fill+1], halfsies[start_day_idx:start_day_fill+1], c=[0.0, 0.0, 0.0], alpha=0.7)
    pl.plot(tvec[start_day_fill:end_day_idx], halfsies[start_day_fill:end_day_idx], c=[0.5, 0.5, 0.5], label=label, lw=4, alpha=0.5)
    pl.plot(tvec[start_day_fill:end_day_idx], halfsies[start_day_fill:end_day_idx], c=main_colour, label=label, lw=2, alpha=1.0)

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


import matplotlib.cm as cm
import matplotlib as mpl 

num_cases = len(list_of_files)
num_cases = num_cases

cmap = cm.get_cmap('YlOrRd', num_cases+1)

norm_cbar = mpl.colors.Normalize(vmin=0,vmax=num_cases)     

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm_cbar)
sm.set_array([])

start_display_day = '2021-02-02' 
# Load the data
pl.plot([0, 58], [5, 5], c=[0.0, 0.0, 0.0], lw=8, alpha=0.5)

for file_idx, this_file in enumerate(list_of_files):
    msim = sc.loadobj(f'{results_folder}/{this_file}')
    sims = msim.sims
    format_ax(ax1, sims[0], start_day_idx=sims[0].day(start_display_day))
    main_colour =  list(cmap(file_idx/len(list_of_files)))[0:-1]
    plotter('new_infections', sims, ax1, label='model predictions', ylabel=r'new daily infections', start_day=start_display_day, main_colour=main_colour)

#plt.yscale('log')
plt.ylim([0.0, 25])
plt.xlim([0.0, 58])


#plot_intervs(sims[0])
cbar = plt.colorbar(sm, ticks=np.linspace(0.5, num_cases-0.5, num_cases), 
                        boundaries=np.arange(0, num_cases+1, 1))

cbar_labels = [f'{np.round(label):.0f}' for label in np.linspace(1.0, 15.0, num_cases)]

cbar.ax.get_yaxis().labelpad = 20
cbar.ax.set_ylabel('cluster size', rotation=270)
cbar.ax.set_yticklabels(cbar_labels)  # vertically oriented colorbar
ax = plt.gca()
# Ancestral strain
ax.annotate('A', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
#ax.annotate('A.2.2', xy=(48., 23), xycoords='data', fontsize=18)
ax.annotate('ancestral', xy=(46., 23), xycoords='data', fontsize=18)


# UK variant
# ax.annotate('B', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
# ax.annotate('B.1.1.7', xy=(48., 23), xycoords='data', fontsize=18)
# ax.annotate('alpha', xy=(48., 23), xycoords='data', fontsize=18)


# Delta variant
# ax.annotate('C', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
# ax.annotate('B.1.617.2', xy=(46., 23), xycoords='data', fontsize=18)
# ax.annotate('delta', xy=(46., 23), xycoords='data', fontsize=18)

ax.annotate('SCT threshold',
            xy=(2., 5.5), xycoords='data',
            #xy=(37., 5.5), xycoords='data',
            xytext=(10, 30), textcoords='offset points',
            arrowprops=dict(arrowstyle="->", connectionstyle="angle,angleA=-180,angleB=90,rad=10"),fontsize=18)
plt.tight_layout()
import covasim as cv
cv.savefig("/".join((figure_folder, figure_filename)), dpi=300)
plt.show()
