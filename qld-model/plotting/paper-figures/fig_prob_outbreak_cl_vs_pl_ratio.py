#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.9)
#mpl.rc('xtick', labelsize=16) 


# Import data - x4 main scenarios 
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')

def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 8360
iq_factor = 0.5

dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)


fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT]$_{B.1.1.7}$/P[SCT]$_{A.2.2}$')
ratio_cl = np.array(dfcluk["resurgence_prob"])/np.array(dfcloz["resurgence_prob"])
ls1 = ax1.plot(dfcluk["cluster_size"], ratio_cl, color="black", lw=0.5)
ls1 = ax1.scatter(dfcluk["cluster_size"], ratio_cl, s=140, color="black", label='A.2.2.')

ls2 = ax1.plot(dfcluk["cluster_size"]-1, np.ones(dfcluk["cluster_size"].shape), color="#1b9e77", lw=6, alpha=0.4)
ax1.set_xlim([0, 18])
ax1.annotate('D', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
fig.tight_layout()
figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
cv.savefig(f"{figure_folder}/fig02_d_prob_sct_ratio_cluster_A22_vs_B117_numtests_{num_tests}.png", dpi=300)
plt.show()
