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
nswcalib = sc.loadobj('nswcalib.msim')

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
pl.figure(figsize=(24,15))

# Extract a sim to refer to
sims = nswcalib.sims
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

# a: daily diagnoses
x0, y0, dx, dy = xgaps, ygaps*2+1*mainplotheight, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])
format_ax(ax1, sim)
plotter('new_diagnoses', sims, ax1, calib=True, label='Model', ylabel='Daily diagnoses')
plot_intervs(sim)

# b. cumulative diagnoses
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*2+1*mainplotheight, subplotwidth, mainplotheight
ax2 = pl.axes([x0, y0, dx, dy])
format_ax(ax2, sim)
plotter('cum_diagnoses', sims, ax2, calib=True, label='Model', ylabel='Cumulative diagnoses')
pl.legend(loc='lower right', frameon=False)

# c. deaths
x0, y0, dx, dy = xgaps, ygaps*1+0*mainplotheight, mainplotwidth, mainplotheight
ax3 = pl.axes([x0, y0, dx, dy])
format_ax(ax3, sim)
plotter('cum_deaths', sims, ax3, calib=True, label='Model', ylabel='Cumulative deaths')
pl.legend(loc='lower right', frameon=False)

# d. active and cumulative infections
x0, y0, dx, dy = xgaps*2.1+mainplotwidth, ygaps*1+0*mainplotheight, subplotwidth, mainplotheight
ax4 = pl.axes([x0, y0, dx, dy])
format_ax(ax4, sim)
plotter('cum_infections', sims, ax4, calib=True, label='Cumulative infections (modeled)', ylabel='Infections')
plotter('n_infectious', sims, ax4, calib=True, label='Active infections (modeled)', ylabel='Infections', flabel=False)
pl.legend(loc='upper left', frameon=False)
#pl.ylim([0, 10e3])

# Add histogram
'''
age_data = pd.read_csv('/Users/robynstuart/Documents/git/covasim-australia/applications/NSW/NSW_AgeHist.csv')

agehists = []

for s,sim in enumerate(sims):
    agehist = cv.age_histogram(days = [sim.day('2020-03-09'), sim.day('2020-04-24')], edges=np.linspace(0,70,15), sim=sim)
    agehists.append(agehist.hists[-1])
x = age_data['age'].values
pos = age_data['cum_diagnoses'].values

# From the model
mposlist = []
for hists in agehists:
    mposlist.append(hists['diagnosed'])
mposarr = np.array(mposlist)
low_q = 0.1
high_q = 0.9
mpbest = pl.median(mposarr, axis=0)
mplow  = pl.quantile(mposarr, q=low_q, axis=0)
mphigh = pl.quantile(mposarr, q=high_q, axis=0)

# Plotting
w = 4
off = 2
bins = x.tolist() + [100]

x0s, y0s, dxs, dys = 0.105, 0.84, 0.17, 0.13
ax1s = pl.axes([x0s, y0s, dxs, dys])
# ax = pl.subplot(4,2,7)
c1 = [0.3,0.3,0.6]
c2 = [0.6,0.7,0.9]
xx = x+w-off
pl.bar(x-off,pos, width=w, label='Data', facecolor=c1)
pl.bar(xx, mpbest, width=w, label='Model', facecolor=c2)
for i,ix in enumerate(xx):
    pl.plot([ix,ix], [mplow[i], mphigh[i]], c='k')
ax1s.set_xticks(np.arange(0,81,20))
pl.xlabel('Age')
pl.ylabel('Cases')
sc.boxoff(ax1s)
pl.legend(frameon=False, bbox_to_anchor=(0.7,1.1))
'''

cv.savefig('calibration.png', dpi=100)

sc.toc(T)