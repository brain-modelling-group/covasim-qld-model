#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper")

# Import data 
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
#df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1

fig, ax1 = plt.subplots(figsize=(6,3.6))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[outbreak detection] [%]')
ax1.set_xlim([1, 10])

category_colors = plt.get_cmap('coolwarm')(np.linspace(0.25, 0.75, 3))

ls1 = []
for idx, nt in enumerate([4160, 6260, 12560]):
    data = get_subframe(df_cluk, nt, iq_factor)
    ls1.append(ax1.plot(data["cluster_size"], data["outbreak_prob"], color=category_colors[idx, ...]*0.8, lw=2, label=str(nt)))


# Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc="lower right", frameon=True, title='number of daily tests')
fig.tight_layout()
cv.savefig(f"fig_prob_outbreak_cluster_tests_iq_0.1.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)