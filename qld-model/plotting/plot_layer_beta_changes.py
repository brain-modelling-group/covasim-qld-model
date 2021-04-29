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
import matplotlib.dates as mdates
import matplotlib.cm as cm
from matplotlib.dates import MO
import datetime # current date and time

import covasim.misc as cvm

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
ax1 = ax.twiny()

norm = mpl.colors.Normalize(vmin=0, vmax=2)
cmap = cm.coolwarm
m = cm.ScalarMappable(norm=norm, cmap=cmap)

yticks = []
yticklabels = []
for layer_idx, this_layer in enumerate(layers):
    for day_idx in range(366+31+22):
        policy_start = beta_data["date"][day_idx]
        ax.broken_barh([(day_idx, 1)], (5*layer_idx, 3), facecolors=m.to_rgba(beta_data[this_layer][day_idx]))
    
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

#import pdb; pdb.set_trace()
plt.tight_layout()

plt.show()