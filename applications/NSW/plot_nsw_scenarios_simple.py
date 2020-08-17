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
resultsfolder = 'results'
figsfolder = 'figs'

maskbetas = [0.6, 0.65, 0.7] # Values used in the scenarios

T = sc.tic()

# Set up lists for storing results to be plotting
diagprobs = []
infprobs = []
diagvals = []
infvals = []
layer_counts = []
layer_remap = {'H': 0, 'S': 1, 'W': 2, 'church': 3, 'pSport': 3, 'cSport': 3, 'social': 3, 'C': 4, 'entertainment': 4,
               'cafe_restaurant': 4, 'pub_bar': 4, 'transport': 4, 'public_parks': 4, 'large_events': 4,
               'importation': 4}
n_new_layers = 5  # H, S, W, DC, SC
colors = sc.gridcolors(n_new_layers)

# Load objects
for i,jb in enumerate(maskbetas):

    # Load in scenario multisims
    msim = sc.loadobj(f'{resultsfolder}/nsw_scenarios_{int(jb*100)}.obj')

    # Calculate probabilities
    diagprobs.append([len([i for i in range(100) if msim.sims[i].results['new_diagnoses'].values[-1]>j])/100 for j in range(500)])
    infprobs.append([len([i for i in range(100) if msim.sims[i].results['n_exposed'].values[-1]>j])/100 for j in range(6000)])
    diagvals.append(msim.sims[0].results['new_diagnoses'].values[-60:])
    infvals.append(msim.sims[0].results['n_exposed'].values[-60:])
    msim.reduce()
    if jb == 0.7: # Save these as the main scenario
        sims = msim.sims
        sim = sims[0]

    # Now load the individual runs that contain the people for making transmission trees
    sim = sc.loadobj(f'results/nsw_scenarios_{int(jb*100)}_single.obj')
    tt = sim.make_transtree()
    layer_keys = list(sim.people.layer_keys()) + ['importation']
    layer_counts.append(np.zeros((sim.npts, n_new_layers)))
    for source_ind, target_ind in tt.transmissions:
        dd = tt.detailed[target_ind]
        date = dd['date']
        layer_num = layer_remap[dd['layer']]
        layer_counts[-1][date, layer_num] += sim.rescale_vec[date]

# Sum transmission by layer over the relevant date ranges
jun01 = cv.date('2020-06-01')
aug15 = cv.date('2020-08-15')
jun01d = sim.day(jun01)
aug15d = sim.day(aug15)
pre_counts = [layer_counts[j][jun01d:aug15d, :].sum(axis=0) for j in range(3)]
post_counts = [layer_counts[j][aug15d:, :].sum(axis=0) for j in range(3)]
pre_counts = [pre_counts[j]/pre_counts[j].sum()*100 for j in range(3)]
post_counts = [post_counts[j]/post_counts[j].sum()*100 for j in range(3)]

# Fonts and sizes
font_size = 22
font_family = 'Proxima Nova'
pl.rcParams['font.size'] = font_size
pl.rcParams['font.family'] = font_family
pl.figure(figsize=(24,15))
pieargs = dict(startangle=90, counterclock=False, labeldistance=1.25)

labels = ['Household', 'School', 'Workplace', 'Known community', 'Unknown community']
ygaps = 0.06
xgaps = 0.06
remainingy = 1-3*ygaps
remainingx = 1-3*xgaps
mainplotheight = remainingy/2
mainplotwidth = remainingx/2

# A. Probabilities of exceeding N daily diagnoses
x0, y0, dx, dy = xgaps, ygaps*2+mainplotheight, mainplotwidth, mainplotheight
ax1 = pl.axes([x0, y0, dx, dy])
colors = pl.cm.GnBu([0.9,0.6,0.3])
ax1.plot(range(300), diagprobs[0][:300], '-', lw=4, c=colors[0], alpha=1.0)
ax1.plot(range(300), diagprobs[1][:300], '-', lw=4, c=colors[1], alpha=1.0)
ax1.plot(range(300), diagprobs[2][:300], '-', lw=4, c=colors[2], alpha=1.0)
ax1.minorticks_on()
pl.grid(which='minor', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
pl.grid(which='major', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
ax1.set_ylim(0,1)
pl.ylabel('Probability of more than n\ndaily cases within 4 weeks')
sc.boxoff(ax=ax1)

# B. Probabilities of exceeding N active cases
x0, y0, dx, dy = xgaps*2+mainplotwidth, ygaps*2+mainplotheight, mainplotwidth, mainplotheight
ax2 = pl.axes([x0, y0, dx, dy])
colors = pl.cm.hot([0.3,0.5,0.7])
ax2 = pl.axes([x0, y0, dx, dy])
ax2.plot(range(6000), infprobs[0], '-', lw=4, c=colors[0], alpha=1.0)
ax2.plot(range(6000), infprobs[1], '-', lw=4, c=colors[1], alpha=1.0)
ax2.plot(range(6000), infprobs[2], '-', lw=4, c=colors[2], alpha=1.0)
ax2.set_ylim(0,1)
ax2.minorticks_on()
pl.grid(which='minor', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
pl.grid(which='major', c=[0, 0, 0], linestyle='--', alpha=0.3, lw=1)
pl.ylabel('Probability of more than n active\ninfections within 4 weeks')
sc.boxoff(ax=ax2)

# Pie charts
x0, y0, dx, dy = xgaps, ygaps, mainplotwidth, mainplotheight
pie_ax1 = pl.axes([x0, y0, dx, dy])
x0, y0, dx, dy = xgaps*2+mainplotwidth, ygaps, mainplotwidth, mainplotheight
pie_ax2 = pl.axes([x0, y0, dx, dy])
colors = sc.gridcolors(n_new_layers)

lpre = [
    f'Household\n{pre_counts[0][0]:0.1f}%',
    f'School\n{pre_counts[0][1]:0.1f}% ',
    f'Workplace\n{pre_counts[0][2]:0.1f}%    ',
    f'Known community\n{pre_counts[0][3]:0.1f}%',
    f'Unknown community\n{pre_counts[0][4]:0.1f}%',
]

lpost = [
    f'Household\n{post_counts[0][0]:0.1f}%',
    f'School\n{post_counts[0][1]:0.1f}%',
    f'Workplace\n{post_counts[0][2]:0.1f}%',
    f'Known community\n{post_counts[0][3]:0.1f}%',
    f'Unknown community\n{post_counts[0][4]:0.1f}%',
]

pie_ax1.pie(pre_counts[0], colors=colors, labels=lpre, **pieargs)
pie_ax2.pie(post_counts[0], colors=colors, labels=lpost, **pieargs)

cv.savefig(f'{figsfolder}/nsw_scenarios_ts.png', dpi=100)

'''


# Plot locations
ygaps = 0.06
xgaps = 0.06
remainingy = 1-2*ygaps
remainingx = 1-2*xgaps
mainplotheight = remainingy
mainplotwidth = remainingx/2


cv.savefig(f'{figsfolder}/nsw_scenarios_simple.png', dpi=100)
'''
sc.toc(T)