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
num_tests = 8360
iq_factor = 0.5

dfploz = get_subframe(df_ploz, num_tests, iq_factor)
dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfpluk = get_subframe(df_pluk, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)


fig, ax1 = plt.subplots(figsize=(6,3.6))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outbreak|cs=x]-P[outbreak|cs=1]')
diff_op_cl = dfcluk["outbreak_prob"]-np.array(dfcluk["outbreak_prob"])[0]

#import pdb; pdb.set_trace()
ls1 = ax1.plot(dfcluk["cluster_size"], diff_op_cl, color="blue", lw=3, label='outbreak detection')

diff_rp_cl = dfcluk["resurgence_prob"]-np.array(dfcluk["resurgence_prob"])[0]
ls3 = ax1.plot(dfcluk["cluster_size"], diff_rp_cl, color="red", lw=3, label='outbreak occurrence')

ax1.set_xlim([1, 15])


# # Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc=0, frameon=False)#)title='ax.legend')
fig.tight_layout()

cv.savefig(f"fig_prob_outbreak_differential_2_UK_cl_{num_tests}.png", dpi=300)
plt.show()