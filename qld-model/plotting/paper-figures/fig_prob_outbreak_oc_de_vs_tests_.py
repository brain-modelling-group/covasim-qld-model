#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster", font_scale=0.8)


# Import data 
#df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_cloz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
iq_factor = 0.1

fig, ax1 = plt.subplots(figsize=(12,7))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('days to outbreak detection')
#ax1.set_ylabel('P[occurrence] [%]')
#ax1.set_ylabel('P[outbreak] [%]')
#ax1.set_ylabel('P[occurrence]/P[detection]')
#ax1.set_ylabel('P[occurrence]-P[detection] [%]')

ax1.set_xlim([1, 15])
#ax1.set_ylim([0, 100])

category_colors = plt.get_cmap('coolwarm')(np.linspace(0.25, 0.75, 5))

ls1 = []
ls2 = []
ls3 = []
for idx, nt in enumerate([6260]):
    data = get_subframe(df_cloz, nt, iq_factor)
    #ls1.append(ax1.plot(data["cluster_size"], data["resurgence_prob"]-(data["outbreak_prob"]), color=[0.2,0.2,0.2], lw=2, label=str(nt)+" [wild strain]"))
    ls2.append(ax1.plot(data["cluster_size"], data["outbreak_day_av"], color=[0.2,0.2,0.2], lw=2, ls='-',label="P[o] "+str(nt)+" [wild strain]"))
    #ls3.append(ax1.plot(data["cluster_size"], data["outbreak_prob"], color=[0.2, 0.2, 0.2], lw=2, ls=':',label= "P[d]" + str(nt)+" [wild strain]"))

category_colors = plt.get_cmap('coolwarm')(np.linspace(0.0, 1.0, 9))
for idx, nt in enumerate([6260, 8360, 10460, 12560]):
    data = get_subframe(df_cluk, nt, iq_factor)
    #ls1.append(ax1.plot(data["cluster_size"], data["resurgence_prob"]-(data["outbreak_prob"]), color=category_colors[idx+5, ...]*0.8, lw=2, label=str(nt)+" [UK variant]"))
    ls2.append(ax1.plot(data["cluster_size"], data["outbreak_day_av"], color=category_colors[idx+5, ...]*0.8, lw=2, ls='-',label="P[o] "+str(nt)+" [UK variant]"))
    #ls3.append(ax1.plot(data["cluster_size"], data["outbreak_prob"], color=category_colors[idx+5, ...]*0.8, lw=2, ls=':',label="P[d] "+str(nt)+" [UK variant]"))


# Labels for legend
handler1, label1 = ax1.get_legend_handles_labels()
ax1.legend(handler1, label1, loc="lower right", frameon=True, title='number of daily tests')
fig.tight_layout()
cv.savefig(f"fig_day_to_outbreak_de_cluster_tests_iq_0.1_uk-oz.png", dpi=300)

plt.show()


#ax2.tick_params(axis='y', labelcolor=color)