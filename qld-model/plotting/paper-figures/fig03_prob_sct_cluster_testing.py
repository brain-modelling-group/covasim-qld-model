#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.5)


# Import data 
#df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')

def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1

fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT] (%)')
ax1.set_xlim([1, 10])
ax1.set_ylim([0, 100])
	
ls1 = []
fake_labels = ['6,000', '8,000', '12,000', '31,000', '100,000']
for idx, nt in enumerate([6260]):
    data = get_subframe(df_cloz, nt, iq_factor)
    ls1.append(ax1.plot(data["cluster_size"], data["resurgence_prob"], color=[0.5, 0.5, 0.5,], ls='--', lw=2, label="~6,000 - A.2.2"))

category_colors = plt.get_cmap('coolwarm')(np.linspace(0.0, 1.0, 11))
for idx, nt in enumerate([6260, 8360, 12560, 31460, 107060]):
    data = get_subframe(df_cluk, nt, iq_factor)
    ls1.append(ax1.plot(data["cluster_size"], data["resurgence_prob"], color=category_colors[10-idx, ...]*0.8, lw=2, label="~"+fake_labels[idx]+" - B.1.1.7"))


# Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc="lower right", frameon=True, title='number of daily tests')
fig.tight_layout()
figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
cv.savefig(f"{figure_folder}/fig03_prob_sct_cluster_tests_iq_0.1_uk-oz.png", dpi=300)

plt.show()
