#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

#for every extra person in the cluster the probability of X increases by Y or is it nonlinear

# Import data - x4 main scenarios 
df_ploz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_oz.csv')
df_pluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_uk.csv')
df_cloz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')

def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 10460
iq_factor = 0.5

dfcluk_06 = get_subframe(df_cluk, 6260, iq_factor)
dfcluk_08 = get_subframe(df_cluk, 8360, iq_factor)
dfcluk_10 = get_subframe(df_cluk, 10460, iq_factor)


fig, ax1 = plt.subplots(figsize=(6,3.6))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outb. occurrence]/P[outb. detection]')

ls1 = ax1.plot(dfcluk_06["cluster_size"], dfcluk_06["resurgence_prob"]/dfcluk_06["outbreak_prob"], color=[0.3,0.3,0.3], lw=3, label='6260')
ls3 = ax1.plot(dfcluk_06["cluster_size"], dfcluk_08["resurgence_prob"]/dfcluk_08["outbreak_prob"], color=[0.5,0.5,0.5], lw=3, label='8360')
ls3 = ax1.plot(dfcluk_06["cluster_size"], dfcluk_10["resurgence_prob"]/dfcluk_10["outbreak_prob"], color=[0.7,0.7,0.7], lw=3, label='10460')

ls4 = ax1.plot(dfcluk_06["cluster_size"], np.ones(dfcluk_06["cluster_size"].shape), color="green", ls='--')
ax1.set_xlim([1, 15])


# # Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc=0, frameon=True, title='number of daily tests')
fig.tight_layout()

cv.savefig(f"fig_prob_outbreak_differential_3_UK_cl_vs_tests.png", dpi=300)
plt.show()