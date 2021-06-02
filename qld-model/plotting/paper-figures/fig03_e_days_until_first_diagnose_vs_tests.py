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
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
#df_cloz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')

def get_subframe(df, cluster_size, iq_factor):
    return df[(df["cluster_size"] == cluster_size) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1
cluster_size = 1

fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('number of daily tests')
ax1.set_ylabel('days until \nfirst confirmed case', labelpad=15)
ax1.set_xscale('log')
ax1.set_xlim([6000, 33000])
ax1.set_ylim([0, 30])
	


ls1 = []
# for idx, nt in enumerate([6260]):
#    

data = get_subframe(df_cluk, cluster_size, iq_factor)

num_tests_x = np.array(data["num_tests"])
sorted_dx_idx = np.argsort(num_tests_x)
num_days_y =  np.array(np.round(data["first_case_day_av"]))
num_days_sd = np.array(np.round(data["first_case_day_sd"]))

ls1.append(ax1.plot(num_tests_x[sorted_dx_idx], num_days_y[sorted_dx_idx], color=[0.5, 0.5, 0.5],  marker='o', ms=10, lw=0.5, alpha=1.0, label="B.1.1.7"))

ax1.fill_between(num_tests_x[sorted_dx_idx], num_days_y[sorted_dx_idx]+num_days_sd[sorted_dx_idx], 
                                        y2=num_days_y[sorted_dx_idx]-num_days_sd[sorted_dx_idx], facecolor=[0.5, 0.5, 0.5], alpha=0.6)



#ax1.annotate("A", xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=22)

# Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc="lower right", frameon=True, title='number of daily tests')
fig.tight_layout()
figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
figure_folder = '/home/paula/data_ext4/Dropbox/COVID/articles/coronavirus-qld-calibration/figures'

#cv.savefig(f"{figure_folder}/fig03_a_prob_sct_cluster_tests_iq_0.1_uk-oz.png", dpi=300)

plt.show()
