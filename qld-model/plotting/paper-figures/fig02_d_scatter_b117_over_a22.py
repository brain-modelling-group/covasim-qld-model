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
df_cloz = pd.read_csv('../../results/csv-data/outbreak_cluster_size_a22.csv')
df_cluk = pd.read_csv('../../results/csv-data/outbreak_cluster_size_b117.csv')
df_clin = pd.read_csv('../../results/csv-data/outbreak_cluster_size_b16172.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 8360
iq_factor = 0.5

dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)
dfclin = get_subframe(df_clin, num_tests, iq_factor)


fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT]$_{variant}$/P[SCT]$_{A.2.2}$')
ratio_cl_b117_a22 = np.array(dfcluk["resurgence_prob"])/np.array(dfcloz["resurgence_prob"])
ratio_cl_b16172_a22 = np.array(dfclin["resurgence_prob"])/np.array(dfcloz["resurgence_prob"])[0:20]

ls2 = ax1.plot(dfcluk["cluster_size"]-1, np.ones(dfcluk["cluster_size"].shape), color="black", lw=6, alpha=0.2)

ls1 = ax1.plot(dfcluk["cluster_size"], ratio_cl_b117_a22, color="black", lw=0.5)
lsx = ax1.plot(dfclin["cluster_size"], ratio_cl_b16172_a22, color="red", lw=0.5)

ls1 = ax1.scatter(dfcluk["cluster_size"], ratio_cl_b117_a22, s=140, color="black", label='A.2.2.')
ls1 = ax1.scatter(dfclin["cluster_size"], ratio_cl_b16172_a22, s=140, color="red", label='A.2.2.')


ax1.set_xlim([0, 18])
ax1.set_ylim([0.8, 4])

ax1.annotate('D', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
fig.tight_layout()
figure_folder = 'fig-files/'
cv.savefig(f"{figure_folder}/fig02_d_prob_sct_ratio_cluster_A22_vs_B117_vs_B16172_numtests_{num_tests}.png", dpi=300)
plt.show()
