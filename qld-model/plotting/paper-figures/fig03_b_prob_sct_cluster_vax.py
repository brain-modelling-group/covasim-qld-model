#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.5)

# Import data 
df_ukvax = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/sct_cluster_vax_b117.csv')
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')

def get_oz_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]


def get_subframe(df, vax_prop, iq_factor):
    return df[(df["vax_proportion"] == vax_prop) & (df["iq_factor"] == iq_factor)]

def get_subsubframe(df, vax_eff):
    return df[(df["vax_efficacy"] == vax_eff)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1
vax_prop  = 0.5

fig, ax1 = plt.subplots(figsize=(9,5.5))
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT] (%)', labelpad=15)
ax1.set_xlim([1, 10])
ax1.set_ylim([0, 100])
    

ls1 = []
data_oz = get_oz_subframe(df_cloz, 6260, iq_factor)
data = get_subframe(df_ukvax, vax_prop, iq_factor)

# Get baseline case
data_baseline =  get_subsubframe(get_subframe(df_ukvax, 0.0, 0.1), 0.0)   

ls1.append(ax1.plot(data_oz["cluster_size"], data_oz["resurgence_prob"], color='black', lw=0.5,  marker='o', ms=10, label="vp, ve = (0%, 0%) - A.2.2"))
ls1.append(ax1.plot(data_baseline["cluster_size"], data_baseline["sct_prob"], color='red', lw=0.5,  marker='o', ms=10, label="vp, ve = (0%, 0%) - B.1.1.7"))

fake_labels = ['vp, ve = (50%, 30%)', 'vp, ve = (50%, 50%)', 'vp, ve = (50%, 70%)', 'vp, ve = (50%, 90%)']
category_colors = plt.get_cmap('Reds_r')(np.linspace(0.0, 1.0, 7))
for idx, ve in enumerate([0.3, 0.5, 0.7, 0.9]):
    data = get_subsubframe(get_subframe(df_ukvax, 0.5, iq_factor), ve) 
    ls1.append(ax1.plot(data["cluster_size"], data["sct_prob"], color=category_colors[idx+2, ...]*0.8, lw=2, label=fake_labels[idx]))


fake_labels = ['vp, ve = (70%, 70%)', 'vp, ve = (70%, 90%)']
category_colors = plt.get_cmap('Blues_r')(np.linspace(0.0, 1.0, 7))
for idx, ve in enumerate([0.7, 0.9]):
    data = get_subsubframe(get_subframe(df_ukvax, 0.7, iq_factor), ve) 
    ls1.append(ax1.plot(data["cluster_size"], data["sct_prob"], color=category_colors[idx+4, ...]*0.8, lw=2, label=fake_labels[idx]))

fake_labels = ['vp, ve = (100%, 90%)']
category_colors = plt.get_cmap('Greens_r')(np.linspace(0.0, 1.0, 7))
for idx, ve in enumerate([0.9]):
    data = get_subsubframe(get_subframe(df_ukvax, 1.0, iq_factor), ve) 
    ls1.append(ax1.plot(data["cluster_size"], data["sct_prob"], color=category_colors[idx+5, ...]*0.8, lw=2, label=fake_labels[idx]))

fake_labels = ['vp, ve = (100%, 100%)']
category_colors = plt.get_cmap('Greens_r')(np.linspace(0.0, 1.0, 7))
for idx, ve in enumerate([1.0]):
    data = get_subsubframe(get_subframe(df_ukvax, 1.0, iq_factor), ve) 
    ls1.append(ax1.plot(data["cluster_size"], data["sct_prob"], color=category_colors[idx+2, ...]*0.8, lw=2, label=fake_labels[idx]))


ax1.annotate("B", xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=22)

# # Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc="lower right", frameon=True, title='')
fig.tight_layout()
#figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
figure_folder = '/home/paula/Dropbox/COVID/articles/coronavirus-qld-calibration/figures'

#cv.savefig(f"{figure_folder}/fig03_b_prob_sct_cluster_vax_iq_0.1_uk.png", dpi=300)

plt.show()
