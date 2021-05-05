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


fig, ax1 = plt.subplots(figsize=(6,3.6))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outb. detec. UK]/P[outb. detec. QLD]')
ratio_cl = np.array(dfcluk["outbreak_prob"])/np.array(dfcloz["outbreak_prob"])
ls1 = ax1.plot(dfcluk["cluster_size"], ratio_cl, color="blue", lw=2)
ls2 = ax1.plot(dfcluk["cluster_size"], np.ones(dfcluk["cluster_size"].shape), color="black", ls='--', label='Cluster seeding')
ax1.set_xlim([1, 35])
#ax1.set_ylim([0, 35])


ax2 = ax1.twiny()  # instantiate a second axes that shares the same y-axis
ax2.set_xlabel('daily imported infections')
color = 'tab:red'
ratio_pl = np.array(dfpluk["outbreak_prob"])/np.array(dfploz["outbreak_prob"])
ls2 = ax2.scatter(dfploz["poisson_lambda"], ratio_pl, color='blue', ls='.-', label='Poisson seeding')

# Labels for legend
lbs = [ls1, ls2]
labs = [l.get_label() for l in lbs]
ax1.legend(lbs, labs, loc=0, frameon=False)
fig.tight_layout()
#cv.savefig(f"fig_prob_outbreak_ratio_QLD_UK_tests_{num_tests}.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)