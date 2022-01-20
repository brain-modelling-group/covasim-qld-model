#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.5)

# Import data 
df_ukvax = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/sct_cluster_vax_b117-n1000.csv')
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')

def get_oz_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

def get_subframe(df, vax_prop, iq_factor):
    return df[(df["vax_proportion"] == vax_prop) & (df["iq_factor"] == iq_factor)]

def get_subsubframe(df, vax_eff):
    return df[(df["vax_efficacy"] == vax_eff)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1
vax_eff  = 0.9

fig, ax1 = plt.subplots(figsize=(9,5.5))
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT] (%)', labelpad=15)
ax1.set_xlim([1, 10])
ax1.set_ylim([0, 100])
    

ls1 = []
ls2 = []

# Get anscestral case
data_oz = get_oz_subframe(df_cloz, 6260, iq_factor)
# Get baseline uk case
data_uk = get_oz_subframe(df_cluk, 6260, iq_factor)
category_colors = plt.get_cmap('coolwarm_r')(np.linspace(0.0, 1.0, 7))

# Reference cases - no vax - A22 and B117
ls1.append(ax1.plot(data_oz["cluster_size"], data_oz["resurgence_prob"], color=category_colors[-1, ...]*0.8, lw=2.5, label="A.2.2"))
ls1.append(ax1.plot(data_uk["cluster_size"], data_uk["resurgence_prob"], color=category_colors[0, ...]*0.8, lw=2.5, label="B.1.1.7"))

fake_labels = ['vacc. coverage 20%', 'vacc. coverage 50%', 'vacc. coverage 70%']
color_idx = [1, 4, 5] 
c_idx = 0
for idx, vp in enumerate([0.2, 0.5, 0.7]):
    data = get_subsubframe(get_subframe(df_ukvax, vp, iq_factor), vax_eff) 
    ls2.append(ax1.plot(data["cluster_size"], data["sct_prob"], color=category_colors[color_idx[c_idx], ...], lw=2, label=fake_labels[c_idx]))
    c_idx +=1

#ax1.annotate("B", xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=22)

# # Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
leg2 = ax1.legend(handler1[2:], label1[2:], loc="lower right", frameon=False, title='vaccination efficacy 90%', fontsize=14)
leg1 = ax1.legend(handler1[0:2], label1[0:2], loc=(0.42, 0.05), frameon=False, title='no vaccination ', fontsize=14)
ax1.add_artist(leg2)
fig.tight_layout()
#figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
#figure_folder = '/home/paula/Dropbox/COVID/articles/coronavirus-qld-calibration/figures'
figure_folder = 'fig-files'
cv.savefig(f"{figure_folder}/supfig07_prob_sct_cluster_vax_iq_0.1_uk_veff-90.png", dpi=300)

plt.show()
