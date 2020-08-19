import covasim as cv
import pandas as pd
import sciris as sc
import pylab as pl
import numpy as np
from matplotlib import ticker
import datetime as dt
import matplotlib.patches as patches

# Filepaths
resultsfolder = 'results0819'
figsfolder = 'figs'
simsfilepath = f'{resultsfolder}/nsw_calibration.obj'
addhist = False

T = sc.tic()

# Import files
simsfile = sc.loadobj(simsfilepath)

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
    else:
        best = pl.mean(yarr, axis=0)
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
            fill_label = '95% projected interval'
        else:
            fill_label = '95% projected interval'
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
pl.figure(figsize=(24,8))

# Extract a sim to refer to
sims = simsfile.sims
sim = sims[0]

# Plot locations
ygaps = 0.05
xgaps = 0.05
remainingy = 1-2*ygaps
remainingx = 1-3*xgaps
mainplotheight = remainingy
mainplotwidth = 0.5
subplotheight = (mainplotheight-ygaps)/2
subplotwidth = 1-mainplotwidth-2.5*xgaps

# a: daily diagnoses
x0, y0, dx, dy = xgaps, ygaps, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])
format_ax(ax1, sim)
plotter('new_diagnoses', sims, ax1, calib=True, label='Model', ylabel='Daily diagnoses (locally acquired)')
#plotter('new_infections', sims, ax1, calib=True, label='Active infections (modeled)', ylabel='', flabel=False)
plot_intervs(sim)

# b. cumulative diagnoses
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps, subplotwidth, mainplotheight
ax2 = pl.axes([x0, y0, dx, dy])
format_ax(ax2, sim)
plotter('cum_infections', sims, ax2, calib=True, label='Cumulative infections (modeled)', ylabel='', flabel=False)
#plotter('n_infectious', sims, ax2, calib=True, label='Active infections (modeled)', ylabel='', flabel=False)
plotter('cum_diagnoses', sims, ax2, calib=True, label='Cumulative diagnoses (modeled)', ylabel='Locally acquired infections & diagnoses', flabel=False)
pl.legend(loc='upper left', frameon=False)
#pl.ylim([0, 10e3])

# Add histogram
if addhist:
    agehists = []

    for s,sim in enumerate(sims):
        agehist = sim['analyzers'][0]
        if s == 0:
            age_data = agehist.data
        agehists.append(agehist.hists[-1])
    raw_x = age_data['age'].values
    raw_pos = age_data['cum_diagnoses'].values

    x = ["0-29", "30-54", "55+"]
    pos = [raw_pos[0:6].sum(), raw_pos[6:11].sum(), raw_pos[11:].sum()]

    # From the model
    mposlist = []
    for hists in agehists:
        mposlist.append(hists['diagnosed'])
    mposarr = np.array(mposlist)
    low_q = 0.1
    high_q = 0.9
    raw_mpbest = pl.median(mposarr, axis=0)
    raw_mplow  = pl.quantile(mposarr, q=low_q, axis=0)
    raw_mphigh = pl.quantile(mposarr, q=high_q, axis=0)

    mpbest = [raw_mpbest[0:6].sum(), raw_mpbest[6:11].sum(), raw_mpbest[11:].sum()]
    mplow = [raw_mplow[0:6].sum(), raw_mplow[6:11].sum(), raw_mplow[11:].sum()]
    mphigh = [raw_mphigh[0:6].sum(), raw_mphigh[6:11].sum(), raw_mphigh[11:].sum()]

    # Plotting
    w = 0.4
    off = .8
    #bins = x.tolist()

    x0s, y0s, dxs, dys = xgaps+0.6*mainplotwidth, ygaps*2+1.5*mainplotheight, 0.1, 0.15
    ax1s = pl.axes([x0s, y0s, dxs, dys])
    # ax = pl.subplot(4,2,7)
    c1 = [0.3,0.3,0.6]
    c2 = [0.6,0.7,0.9]
    X = np.arange(len(x))
    XX = X+w-off
    pl.bar(X,pos, width=w, label='Data', facecolor=c1)
    pl.bar(XX, mpbest, width=w, label='Model', facecolor=c2)
    #pl.bar(x-off,pos, width=w, label='Data', facecolor=c1)
    #pl.bar(xx, mpbest, width=w, label='Model', facecolor=c2)
    for i,ix in enumerate(XX):
        pl.plot([ix,ix], [mplow[i], mphigh[i]], c='k')
    ax1s.set_xticks((X+XX)/2)
    ax1s.set_xticklabels(x)
    pl.xlabel('Age')
    pl.ylabel('Cases 9 Mar–24 Apr')
    sc.boxoff(ax1s)
    pl.legend(frameon=False, bbox_to_anchor=(0.7,1.1))


cv.savefig(f'{figsfolder}/nsw_calibration.png', dpi=100)

sc.toc(T)