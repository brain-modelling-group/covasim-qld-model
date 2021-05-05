#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

#sns.set_context("paper")
#mpl.rc('xtick', labelsize=16) 


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


fig, ax1 = plt.subplots(figsize=(6,4))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outbreak detection] (%)')
ls1 = ax1.scatter(dfcloz["cluster_size"], dfcloz["outbreak_prob"], color="#2c7fb8", label='QLD/Cluster seeding')
ls2 = ax1.scatter(dfcluk["cluster_size"], dfcluk["outbreak_prob"], color='#fd8d3c', label='UK/Cluster seeding')
ax1.set_xlim([0, 35])

ax2 = ax1.twiny()  # instantiate a second axes that shares the same y-axis
ax2.set_xlabel('daily imported infections')
color = 'tab:red'
ls3 = ax2.scatter(dfploz["poisson_lambda"],dfploz["outbreak_prob"], color='#253494', label='QLD/Poisson seeding ')
ls4 = ax2.scatter(dfpluk["poisson_lambda"],dfpluk["outbreak_prob"], color='#bd0026', label='UK/Poisson seeding')
ax2.set_xlim([0, 3])

# Labels for legend
lbs = [ls1, ls3, ls2, ls4]
labs = [l.get_label() for l in lbs]
ax1.legend(lbs, labs, loc=0, frameon=True)
fig.tight_layout()
cv.savefig(f"fig_prob_outbreak_cl_vs_pl_cases_{num_tests}.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)