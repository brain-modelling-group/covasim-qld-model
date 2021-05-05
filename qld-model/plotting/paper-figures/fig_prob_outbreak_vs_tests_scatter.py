#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster")

# Import data 
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
#df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
iq_factor = 1.0

fig, ax1 = plt.subplots(figsize=(9,7))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('prob outbreak [%]')
ax1.set_xlim([0, 17])

category_colors = plt.get_cmap('inferno')(np.linspace(0.25, 0.75, 5))

ls1 = []
for idx, nt in enumerate([4160, 6260, 8360, 10460, 12560]):
    data = get_subframe(df_cluk, nt, iq_factor)
    ls1.append(ax1.scatter(data["cluster_size"], data["outbreak_prob"], color=category_colors[idx, ...], label=f"{nt}"))


# Labels for legend
labs = [l.get_label() for l in ls1]
ax1.legend(ls1, labs, loc=0, frameon=False)
fig.tight_layout()
#cv.savefig(f"fig_prob_outbreak_cluster_tests_iq_1.0.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)