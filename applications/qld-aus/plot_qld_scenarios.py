#!/usr/bin/env python
# coding: utf-8
"""
Plot QLD results obtained with run_qld_wave_01.py 
=============================================================


# author: For QLD Paula Sanz-Leon, QIMRB, August 2020
#         based on NSW plotting originally written by Robyn Stuart, Optima, 2020
"""

import covasim as cv
import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches

# Filepaths
resultsfolder = 'results'
figsfolder = 'figs'
simsfilepath = f'{resultsfolder}/qld_calibration.obj'

julybetas = [0.05, 0.1, 0.15] # Values used in the scenarios

T = sc.tic()

# Load in scenario multisims
diagprobs = []
infprobs = []
diagvals = []
infvals = []
num_sim_runs = 20

for jb in julybetas:
    msim = sc.loadobj(f'{resultsfolder}/qld_scenarios_{int(jb*100)}.obj')
    diagprobs.append([len([i for i in range(num_sim_runs) if msim.sims[i].results['new_diagnoses'].values[-1]>j])/num_sim_runs for j in range(500)])
    infprobs.append([len([i for i in range(num_sim_runs) if msim.sims[i].results['n_exposed'].values[-1]>j])/num_sim_runs for j in range(6000)])
    diagvals.append(msim.sims[0].results['new_diagnoses'].values[-60:])
    infvals.append(msim.sims[0].results['n_exposed'].values[-60:])
    msim.reduce()
    if jb == julybetas[-1]: # Save these as the main scenario
        sims = msim.sims
        sim = sims[0]


# Define plotting functions
#%% Helper functions

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

def plotter(key, sims, ax, ys=None, calib=False, label='', ylabel='', low_q=0.025, high_q=0.975, flabel=True, startday=None, subsample=2, chooseseed=0):

    which = key.split('_')[1]
    try:
        color = cv.get_colors()[which]
    except:
        color = [0.5,0.5,0.5]
    if which == 'diagnoses':
        color = [0.03137255, 0.37401   , 0.63813918, 1.        ]
    elif which == '':
        color = [0.82400815, 0.        , 0.        , 1.        ]

    if ys is None:
        ys = []
        for s in sims:
            ys.append(s.results[key].values)

    yarr = np.array(ys)
    if chooseseed is not None:
        best = sims[chooseseed].results[key].values
    low  = pl.quantile(yarr, q=low_q, axis=0)
    high = pl.quantile(yarr, q=high_q, axis=0)

    sim = sims[0] # For having a sim to refer to

    tvec = np.arange(len(best))
    if key in sim.data:
        data_t = np.array((sim.data.index-sim['start_day'])/np.timedelta64(1,'D'))
        inds = np.arange(0, len(data_t), subsample)
        pl.plot(data_t[inds], sim.data[key][inds], 'd', c=color, markersize=10, alpha=0.5, label='Data')

    start = None
    if startday is not None:
        start = sim.day(startday)
    end = None
    if flabel:
        if which == 'infections':
            fill_label = '95% projec-\nted interval'
        else:
            fill_label = '95% projected\ninterval'
    else:
        fill_label = None
    pl.fill_between(tvec[startday:end], low[startday:end], high[startday:end], facecolor=color, alpha=0.2, label=fill_label)
    pl.plot(tvec[startday:end], best[startday:end], c=color, label=label, lw=4, alpha=1.0)

    sc.setylim()

    xmin,xmax = ax.get_xlim()
    if calib:
        ax.set_xticks(pl.arange(xmin+2, xmax, 21))
    else:
        ax.set_xticks(pl.arange(xmin+2, xmax, 21))

    pl.ylabel(ylabel)

    return tvec, color


def plot_intervs(sim, labels=True):

    color = [0, 0, 0]
    mar23 = sim.day('2020-03-23')
    may01 = sim.day('2020-05-01')
    jul10 = sim.day('2020-07-10')
    aug05 = sim.day('2020-08-05')

    for day in [mar23, may01, jul10, aug05]:
        pl.axvline(day, c=color, linestyle='--', alpha=0.4, lw=3)

    if labels:
        yl = pl.ylim()
        labely = yl[1]*0.95
        pl.text(mar23-20, labely, 'Lockdown',               color=color, alpha=0.9, style='italic')
        pl.text(may01+1,  labely, 'Begin phased \nrelease', color=color, alpha=0.9, style='italic')
        pl.text(jul10+1,  labely, 'QLD \nborder \nopen',    color=color, alpha=0.9, style='italic')
        pl.text(aug05+1,  labely, 'QLD \nborder \nclosed',  color=color, alpha=0.9, style='italic')
    return

# Fonts and sizes
font_size = 20
# font_family = 'Proxima Nova'
pl.rcParams['font.size'] = font_size
# pl.rcParams['font.family'] = font_family
pl.figure(figsize=(24,15))

# Plot locations
ygaps = 0.03
xgaps = 0.06
remainingy = 1-3*ygaps
remainingx = 1-3*xgaps
mainplotheight = remainingy/2
mainplotwidth = 0.5
subplotheight = (mainplotheight-ygaps)/2
subplotwidth = 1-mainplotwidth-2.5*xgaps

# Plot diagnoses
x0, y0, dx, dy = xgaps, ygaps*2+1*mainplotheight, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])
format_ax(ax1, sim)
tvec, color = plotter('new_diagnoses', sims, ax1, calib=True, label='Model', ylabel='new diagnoses')
plot_intervs(sim)
# Load actual data 
inputs_folder = 'inputs'
input_data = 'qld_epi_data_wave_01_basic_stats.csv'

# Load data
data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])
xx = data['new_cases'][36:-1]
#import ipdb; ipdb.set_trace()
pl.plot(tvec[0:-(tvec.shape[0] - xx.shape[0])], data['new_cases'][36:-1], c=color, label='epi data', lw=4, alpha=0.5)

#Plot diagnoses scenarios
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*3+1*mainplotheight+subplotheight, subplotwidth, subplotheight
ax2 = pl.axes([x0, y0, dx, dy])
#format_ax(ax2, sim)
@ticker.FuncFormatter
def date_formatter(x, pos):
    return (dt.date(2020,7,1) + dt.timedelta(days=x)).strftime('%b-%d')
ax2.xaxis.set_major_formatter(date_formatter)
sc.commaticks()
pl.xlim([0, 60])
sc.boxoff()
tvec = np.arange(60)
#v70 = msim70.base_sim.results['new_diagnoses'].values[-60:]
#v60 = msim60.base_sim.results['new_diagnoses'].values[-60:]
#v50 = msim50.base_sim.results['new_diagnoses'].values[-60:]
colors = pl.cm.GnBu([0.9,0.6,0.3])
pl.plot(tvec, diagvals[0], c=colors[0], '-',  label=str(julybetas[0]), lw=4, alpha=1.0)
pl.plot(tvec, diagvals[1], c=colors[1], '--', label=str(julybetas[1]), lw=4, alpha=1.0)
pl.plot(tvec, diagvals[2], c=colors[2], '-',  label=str(julybetas[2]), lw=4, alpha=1.0)
pl.ylabel('Daily diagnoses')
sc.setylim()
xmin, xmax = ax2.get_xlim()
ax2.set_xticks(pl.arange(xmin + 2, xmax, 7))
pl.legend(loc='upper left', frameon=False)

x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*2+1*mainplotheight, subplotwidth, subplotheight
ax3 = pl.axes([x0, y0, dx, dy])
ax3.plot(range(80), diagprobs[0][:80], '-', lw=4, c=colors[0], alpha=1.0)
ax3.plot(range(80), diagprobs[1][:80], '-', lw=4, c=colors[1], alpha=1.0)
ax3.plot(range(80), diagprobs[2][:80], '-', lw=4, c=colors[2], alpha=1.0)
ax3.set_ylim(0,1)
pl.ylabel('Probability of more\nthan n daily cases')
sc.boxoff(ax=ax3)

# Plot active cases
x0, y0, dx, dy = xgaps, ygaps*1+0*mainplotheight, mainplotwidth, mainplotheight
ax4 = pl.axes([x0, y0, dx, dy])
format_ax(ax4, sim)
plotter('n_exposed', sims, ax4, calib=False, label='Model', ylabel='Active infections')
#pl.legend(loc='upper center', frameon=False)

#Plot active cases scenarios
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*2+0*mainplotheight+subplotheight, subplotwidth, subplotheight
ax5 = pl.axes([x0, y0, dx, dy])
#format_ax(ax2, sim)
@ticker.FuncFormatter
def date_formatter(x, pos):
    return (dt.date(2020,7,1) + dt.timedelta(days=x)).strftime('%b-%d')
ax5.xaxis.set_major_formatter(date_formatter)
sc.commaticks()
pl.xlim([0, 60])
sc.boxoff()
tvec = np.arange(60)
#v70 = msim70.base_sim.results['n_exposed'].values[-60:]
#v60 = msim60.base_sim.results['n_exposed'].values[-60:]
#v50 = msim50.base_sim.results['n_exposed'].values[-60:]
colors = pl.cm.hot([0.3,0.5,0.7])
pl.plot(tvec, infvals[0], c=colors[0], label=str(julybetas[0]), lw=4, alpha=1.0)
pl.plot(tvec, infvals[1], c=colors[1], label=str(julybetas[1]), lw=4, alpha=1.0)
pl.plot(tvec, infvals[2], c=colors[2], label=str(julybetas[2]), lw=4, alpha=1.0)
pl.ylabel('Active infections')
sc.setylim()
xmin, xmax = ax5.get_xlim()
ax5.set_xticks(pl.arange(xmin + 2, xmax, 7))
pl.legend(loc='upper left', frameon=False)

x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*1+0*mainplotheight, subplotwidth, subplotheight
ax6 = pl.axes([x0, y0, dx, dy])
ax6.plot(range(6000), infprobs[0], '-', lw=4, c=colors[0], alpha=1.0)
ax6.plot(range(6000), infprobs[1], '-', lw=4, c=colors[1], alpha=1.0)
ax6.plot(range(6000), infprobs[2], '-', lw=4, c=colors[2], alpha=1.0)
ax6.set_ylim(0,1)
pl.ylabel('Probability of more\nthan n active infections')
sc.boxoff(ax=ax6)


cv.savefig(f'{figsfolder}/qld_scenarios.png', dpi=100)

sc.toc(T)