import covasim as cv
import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches
import matplotlib.dates as mdates

# Filepaths
resultsfolder = 'results0819'
figsfolder = 'figs'

if resultsfolder=='results0819':
    maskbetas_main = [0.59, 0.62, 0.7] # Values used in the scenarios
    maskbetas_sens = [0.55, 0.60, 0.7] # Values used in the scenarios
    maskbetas = maskbetas_main

else:
    maskbetas = [0.6, 0.65, 0.7]
# Main scenarios are with maskeff = 0.23, corresponding to [0.59, 0.62, 0.7]
# Sensitivity analyses with maskeff = 0.3 corresponds to [0.55, 0.6, 0.7]

T = sc.tic()

# Set up lists for storing results to be plotting
diagprobs = []
infprobs = []
inf_med = []
inf_low = []
inf_high = []

# Load objects
for i,jb in enumerate(maskbetas):

    # Load in scenario multisims
    msim = sc.loadobj(f'{resultsfolder}/nsw_scenarios_{int(jb*100)}.obj')

    # Calculate probabilities
    diagprobs.append([len([i for i in range(100) if msim.sims[i].results['new_diagnoses'].values[-1]>j])/100 for j in range(100)])
    infprobs.append([len([i for i in range(100) if msim.sims[i].results['n_exposed'].values[-1]>j])/100 for j in range(1000)])

    # Extract a sim for getting time vectors and so on
    sims = msim.sims
    sim = sims[0]

    # Reduce sim and extract weekly values
    msim.reduce()
    w0, w1, w2, w3, w4 = cv.date('2020-08-18'), cv.date('2020-08-25'), cv.date('2020-09-01'), cv.date('2020-09-08'), cv.date('2020-09-15')
    wd = [sim.day(w0), sim.day(w1), sim.day(w2), sim.day(w3), sim.day(w4)]
    inf_med.append(msim.results['new_diagnoses'].values[wd])
    inf_low.append(msim.results['new_diagnoses'].low[wd])
    inf_high.append(msim.results['new_diagnoses'].high[wd])

# Now load the transmission tree data
tlc = sc.loadobj(f'{resultsfolder}/nsw_layer_counts.obj')
layer_counts = {}
for jb in maskbetas: layer_counts[jb] = tlc[jb].sum(axis=0)/100 # Get mean

# Sum transmission by layer over the relevant date ranges
jun01 = cv.date('2020-06-01')
aug15 = cv.date('2020-08-19')
jun01d = sim.day(jun01)
aug15d = sim.day(aug15)

low_q = 0.1
high_q = 0.9
layer_counts_pre_med  = pl.median(tlc[0.7][:, jun01d:aug15d, :].sum(axis=1), axis=0)
layer_counts_pre_low  = pl.quantile(tlc[jb][:, jun01d:aug15d, :].sum(axis=1), q=low_q, axis=0)
layer_counts_pre_high = pl.quantile(tlc[jb][:, jun01d:aug15d, :].sum(axis=1), q=high_q, axis=0)
for jb in maskbetas:
    layer_counts_med  = [pl.median(tlc[jb][:, aug15d:, :].sum(axis=1), axis=0) for jb in maskbetas]
    layer_counts_low  = [pl.quantile(tlc[jb][:, aug15d:, :].sum(axis=1), q=low_q, axis=0) for jb in maskbetas]
    layer_counts_high = [pl.quantile(tlc[jb][:, aug15d:, :].sum(axis=1), q=high_q, axis=0) for jb in maskbetas]

# Fonts and sizes
font_size = 22
font_family = 'Proxima Nova'
pl.rcParams['font.size'] = font_size
pl.rcParams['font.family'] = font_family
pl.figure(figsize=(24,15))

ygaps = 0.06
xgaps = 0.065
remainingy = 1-3*ygaps
remainingx = 1-3*xgaps
mainplotheight = remainingy/2
mainplotwidth = remainingx/2

# A. Probabilities of exceeding N daily diagnoses
pl.figtext(xgaps*0.2, ygaps*2+mainplotheight*2, 'A', fontsize=40)
x0, y0, dx, dy = xgaps, ygaps*2+mainplotheight, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])
colors = pl.cm.GnBu([0.9,0.6,0.3])
ax1.plot(range(len(diagprobs[0])), diagprobs[0], '-', lw=4, c=colors[0], alpha=1.0)
ax1.plot(range(len(diagprobs[0])), diagprobs[1], '-', lw=4, c=colors[1], alpha=1.0)
ax1.plot(range(len(diagprobs[0])), diagprobs[2], '-', lw=4, c=colors[2], alpha=1.0)
#ax1.minorticks_on()
#pl.grid(which='minor', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
#pl.grid(which='major', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
ax1.set_ylim(0,1)
pl.ylabel('Probability of more than n\ndaily cases within 4 weeks')
sc.boxoff(ax=ax1)

# B. Probabilities of exceeding N active cases
pl.figtext(xgaps*1.2+mainplotwidth, ygaps*2+mainplotheight*2, 'B', fontsize=40)
x0, y0, dx, dy = xgaps*2+mainplotwidth, ygaps*2+mainplotheight, mainplotwidth, mainplotheight
ax2 = pl.axes([x0, y0, dx, dy])
colors = pl.cm.GnBu([0.9,0.6,0.3]) #pl.cm.hot([0.3,0.5,0.7])
ax2 = pl.axes([x0, y0, dx, dy])
ax2.plot(range(len(infprobs[0])), infprobs[0], '-', lw=4, c=colors[0], label="High masks", alpha=1.0)
ax2.plot(range(len(infprobs[0])), infprobs[1], '-', lw=4, c=colors[1], label="Moderate masks", alpha=1.0)
ax2.plot(range(len(infprobs[0])), infprobs[2], '-', lw=4, c=colors[2], label="No masks", alpha=1.0)
ax2.set_ylim(0,1)
#ax2.minorticks_on()
#pl.grid(which='minor', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
#pl.grid(which='major', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
pl.ylabel('Probability of more than n active\ninfections within 4 weeks')
pl.legend(loc='upper right', frameon=False)
sc.boxoff(ax=ax2)

# C. bar chart
pl.figtext(xgaps*0.2, ygaps*1+mainplotheight, 'C', fontsize=40)
x0, y0, dx, dy = xgaps, ygaps, mainplotwidth, mainplotheight
bar_ax = pl.axes([x0, y0, dx, dy])
colors = sc.gridcolors(5)

x = np.arange(5)
colors = [(0.5,0.5,0.5), pl.cm.GnBu(0.3), pl.cm.GnBu(0.6), pl.cm.GnBu(0.9)]
#layers_to_plot_med = [layer_counts_pre_med[0], layer_counts_med[2], layer_counts_med[1], layer_counts_med[0]]
#layers_to_plot_low = [layer_counts_pre_low[0], layer_counts_low[2], layer_counts_low[1], layer_counts_low[0]]
#layers_to_plot_high = [layer_counts_pre_high[0], layer_counts_high[2], layer_counts_high[1], layer_counts_high[0]]
layers_to_plot_med = [layer_counts_med[2], layer_counts_med[1], layer_counts_med[0]]
layers_to_plot_low = [layer_counts_low[2], layer_counts_low[1], layer_counts_low[0]]
layers_to_plot_high = [layer_counts_high[2], layer_counts_high[1], layer_counts_high[0]]
labels = ['Household', 'School', 'Workplace', 'Known\ncommunity', 'Unknown\ncommunity']
#scenlabels = ['Jun 1 - Aug 15', 'Aug 16 - Sep 15: No masks', 'Aug 16 - Sep 15: Moderate masks', 'Aug 16 - Sep 15: Optimistic masks']
scenlabels = ['No masks', 'Moderate masks', 'High masks']

for ltp in range(3):
    bar_ax.bar(x+0.1*ltp-0.3, layers_to_plot_med[ltp], color=colors[ltp+1], width=0.1, label = scenlabels[ltp])
    pl.plot([x+0.1*ltp-0.3,x+0.1*ltp-0.3], [layers_to_plot_low[ltp], layers_to_plot_high[ltp]], c='k')

bar_ax.set_xticks(x-0.15)
bar_ax.set_xticklabels(labels)
#bar_ax.legend(frameon=False)
pl.ylabel('Cumulative infections by layer\nAug 16 - Sep 15')
sc.boxoff(ax=bar_ax)

# D. box plot chart
pl.figtext(xgaps*1.2+mainplotwidth, ygaps*1+mainplotheight, 'D', fontsize=40)
x0, y0, dx, dy = xgaps*2+mainplotwidth, ygaps, mainplotwidth, mainplotheight
box_ax = pl.axes([x0, y0, dx, dy])
x = np.arange(5)
for ltp in range(3):
    box_ax.errorbar(x+0.1*ltp-0.3, inf_med[ltp], yerr=[inf_low[ltp], inf_high[ltp]], fmt='o', color=colors[ltp+1], ecolor=colors[ltp+1], ms=20, elinewidth=3, capsize=0)

box_ax.set_xticks(x-0.15)
#box_ax.set_xticklabels(labels)

@ticker.FuncFormatter
def date_formatter(x, pos):
    return (aug15 + dt.timedelta(days=x*7)).strftime('%b-%d')

box_ax.xaxis.set_major_formatter(date_formatter)
pl.ylabel('Estimated daily infections')
sc.boxoff(ax=box_ax)

#pl.xlim([0, sim['n_days']])
#box_ax.legend(frameon=False)


cv.savefig(f'{figsfolder}/nsw_scenarios_new.png', dpi=100)

sc.toc(T)