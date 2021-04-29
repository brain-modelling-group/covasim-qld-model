#!/usr/bin/env python
# coding: utf-8
"""
Plot bar to visualise changes in beta 
=============================================================

# author: For QLD Paula Sanz-Leon, QIMRB, January 2021
"""
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.dates import MO
import datetime # current date and time
import colorsys


import covasim.misc as cvm



def scale_lightness(rgb, scale_l):
    # convert rgb to hls
    #import pdb; pdb.set_trace()
    h, l, s = colorsys.rgb_to_hls(*rgb[:-1])
    # manipulate h, l, s values and return as rgb
    return colorsys.hls_to_rgb(h, min(1.0, l * scale_l), s=s)

class MidpointNormalize(mcolors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        v_ext = np.max([np.abs(self.vmin), np.abs(self.vmax)])
        x, y = [-v_ext, self.midpoint, v_ext], [-1.0, 0.5, 1.0]
        return np.ma.masked_array(np.interp(value, x, y))

# 
start_date = '2020-01-01'
end_date = '2021-02-22'
duration_length = cvm.day(end_date, start_day=start_date)

# Load empirical data
inputs_folder = 'inputs'
input_data = 'qld_model_layer_betas_02.csv'

# Load data
beta_data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

layers = ['H', 
          'S', 
          'W', 
          'C', 
          'church', 
          'pSport', 
          'cSport', 
          'entertainment', 
          'cafe_restaurant', 
          'pub_bar', 
          'transport', 
          'public_parks', 
          'large_events', 
          'social'] 
# Human readable labels
hr_layers = ['home', 
             'school', 
             'work', 
             'community', 
             'places of worship', 
             'professional sport', 
             'community sport', 
             'entertainment', 
             'cafe restaurant', 
             'pub/bar', 
             'transport', 
             'public parks', 
             'large events', 
             'social'] 

fig, ax = plt.subplots(1,1, figsize=(10,5))


norm = MidpointNormalize(midpoint=1.0, vmin=0.0, vmax=1.2)
cmap = cm.get_cmap('coolwarm', 256)
m = cm.ScalarMappable(norm=norm, cmap=cmap)
# dummy colour data
dummy_y = np.linspace(0.0, 1.2, 256)
dummy_x = np.linspace(-5, -1, 256)

newcolors = [scale_lightness(m.to_rgba(val), 0.7) for val in dummy_y] 
new_cmap = ListedColormap(newcolors)

color_data = ax.scatter(dummy_x, dummy_y, c=dummy_y, cmap=new_cmap, s= 0.1)
fig.colorbar(color_data, ax=ax, orientation='vertical', pad=0.01)

ax1 = ax.twiny()
yticks = []
yticklabels = []

for layer_idx, this_layer in enumerate(layers):
    for day_idx in range(366+31+22):
        policy_start = beta_data["date"][day_idx]
        ax.broken_barh([(day_idx, 1)], (5*layer_idx, 3), facecolors=scale_lightness(m.to_rgba(beta_data[this_layer][day_idx]),0.7))
    yticks.append(5*layer_idx+1.5)
    yticklabels.append(hr_layers[layer_idx]) 

ax.set_ylim(0, 75)
ax.set_xlim(0, 365+31+22)
ax.set_xlabel('days (since Jan 1st 2020)')
ax.set_yticks(yticks)
ax.set_yticklabels(yticklabels)
ax.grid(True)

#ax1.set_xlim(ax.get_xlim())
ax1.set_xlim([datetime.date(2020, 1, 1), datetime.date(2021, 2, 22)])
# Set ticks every week
ax1.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=MO, interval=4))
# Set major ticks format
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
plt.setp(ax1.get_xticklabels(), rotation=30, ha="left", rotation_mode="anchor")

plt.tight_layout()
plt.savefig("plotting/paper-figures/fig_gantt_layer_betas.png",dpi=300)
#plt.show()
