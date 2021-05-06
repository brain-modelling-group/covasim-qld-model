#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster", font_scale=0.8)
#mpl.rc('xtick', labelsize=16) 


# Import data - x4 main scenarios 
df_ploz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_oz.csv')
df_pluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_uk.csv')
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')



def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 8360
iq_factor = 0.5

dfploz = get_subframe(df_ploz, num_tests, iq_factor)
dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfpluk = get_subframe(df_pluk, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)


fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outbreak occurrence] (%)')
ls1 = ax1.scatter(dfcloz["cluster_size"], dfcloz["resurgence_prob"], color="#2c7fb8", label='QLD/Cluster seeding')
ax1.plot(dfcloz["cluster_size"], dfcloz["resurgence_prob"], lw=0.5, color="#2c7fb8", label='QLD/Cluster seeding')

ls2 = ax1.scatter(dfcluk["cluster_size"], dfcluk["resurgence_prob"], color='#fd8d3c', label='UK/Cluster seeding')
ax1.plot(dfcluk["cluster_size"], dfcluk["resurgence_prob"], lw=0.5, color='#fd8d3c', label='UK/Cluster seeding')

ax1.set_xlim([0.5, 15])

# ax2 = ax1.twiny()  # instantiate a second axes that shares the same y-axis
# ax2.set_xlabel('daily imported infections')
# color = 'tab:red'
# ls3 = ax2.scatter(dfploz["poisson_lambda"],dfploz["resurgence_prob"], marker='o', color='#253494', label='QLD/Poisson seeding ')
# ls4 = ax2.scatter(dfpluk["poisson_lambda"],dfpluk["resurgence_prob"], marker='o', color='#bd0026', label='UK/Poisson seeding')
# ax2.set_xlim([0.05, 1.5])
# ax2.set_ylim([0.0, 105])

# Labels for legend
lbs = [ls1, ls2]
#lbs = [ls1, ls3, ls2, ls4]

labs = [l.get_label() for l in lbs]
ax1.legend(lbs, labs, loc=0, frameon=True)
fig.tight_layout()
cv.savefig(f"fig_prob_outbreak_oc_cl_vs_pl_cases_{num_tests}.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)