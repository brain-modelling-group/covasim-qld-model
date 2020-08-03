import covasim as cv
import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches

T = sc.tic()

# Import files
msim70 = sc.loadobj('covasim70.msim')

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

    return


def plot_intervs(sim, labels=True):

    color = [0, 0, 0]
    mar23 = sim.day('2020-03-23')
    may01 = sim.day('2020-05-01')
    jul07 = sim.day('2020-07-07')
    for day in [mar23, may01, jul07]:
        pl.axvline(day, c=color, linestyle='--', alpha=0.4, lw=3)

    if labels:
        yl = pl.ylim()
        labely = yl[1]*0.95
        pl.text(mar23-20, labely, 'Lockdown', color=color, alpha=0.9, style='italic')
        pl.text(may01+1,  labely, 'Begin phased \nrelease', color=color, alpha=0.9, style='italic')
        pl.text(jul07+1,  labely, 'NSW/Victoria \nborder closed', color=color, alpha=0.9, style='italic')
    return


# Fonts and sizes
font_size = 22
font_family = 'Proxima Nova'
pl.rcParams['font.size'] = font_size
pl.rcParams['font.family'] = font_family
pl.figure(figsize=(24,15))

# Extract a sim to refer to
sims = msim70.sims
sim = sims[0]

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
plotter('new_diagnoses', sims, ax1, calib=True, label='Model', ylabel='Daily diagnoses')
plot_intervs(sim)

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
v70 = msim70.base_sim.results['new_diagnoses'].values[-60:]
v60 = msim60.base_sim.results['new_diagnoses'].values[-60:]
v50 = msim50.base_sim.results['new_diagnoses'].values[-60:]
colors = pl.cm.GnBu([0.9,0.6,0.3])
pl.plot(tvec, v70, c=colors[0], label="Without masks", lw=4, alpha=1.0)
pl.plot(tvec, v60, c=colors[1], label="50% mask uptake", lw=4, alpha=1.0)
pl.plot(tvec, v50, c=colors[2], label="70% mask uptake", lw=4, alpha=1.0)
pl.ylabel('Daily diagnoses')
sc.setylim()
xmin, xmax = ax2.get_xlim()
ax2.set_xticks(pl.arange(xmin + 2, xmax, 7))
pl.legend(loc='upper left', frameon=False)

x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*2+1*mainplotheight, subplotwidth, subplotheight
ax3 = pl.axes([x0, y0, dx, dy])
ax3.plot(range(300), listprobs70[:300], '-', lw=4, c=colors[0], alpha=1.0)
ax3.plot(range(300), listprobs60[:300], '-', lw=4, c=colors[1], alpha=1.0)
ax3.plot(range(300), listprobs50[:300], '-', lw=4, c=colors[2], alpha=1.0)
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
v70 = msim70.base_sim.results['n_exposed'].values[-60:]
v60 = msim60.base_sim.results['n_exposed'].values[-60:]
v50 = msim50.base_sim.results['n_exposed'].values[-60:]
colors = pl.cm.hot([0.3,0.5,0.7])
pl.plot(tvec, v70, c=colors[0], label="Without masks", lw=4, alpha=1.0)
pl.plot(tvec, v60, c=colors[1], label="50% mask uptake", lw=4, alpha=1.0)
pl.plot(tvec, v50, c=colors[2], label="70% mask uptake", lw=4, alpha=1.0)
pl.ylabel('Active infections')
sc.setylim()
xmin, xmax = ax5.get_xlim()
ax5.set_xticks(pl.arange(xmin + 2, xmax, 7))
pl.legend(loc='upper left', frameon=False)

#x0, y0, dx, dy = xgaps+.5, ygaps*3+mainplotheight*2.2,  0.25, 0.1
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*1+0*mainplotheight, subplotwidth, subplotheight
ax6 = pl.axes([x0, y0, dx, dy])
ax6.plot(range(6000), actprobs70, '-', lw=4, c=colors[0], alpha=1.0)
ax6.plot(range(6000), actprobs60, '-', lw=4, c=colors[1], alpha=1.0)
ax6.plot(range(6000), actprobs50, '-', lw=4, c=colors[2], alpha=1.0)
ax6.set_ylim(0,1)
pl.ylabel('Probability of more\nthan n active infections')
sc.boxoff(ax=ax6)


cv.savefig('probs.png', dpi=100)

sc.toc(T)