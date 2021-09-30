#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.9)

# Import data - x4 main scenarios 
df_cloz = pd.read_csv('../../results/csv-data/outbreak_cluster_size_a22.csv')
df_cluk = pd.read_csv('../../results/csv-data/outbreak_cluster_size_b117.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 8360
iq_factor = 0.5

dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)


fig, ax1 = plt.subplots(figsize=(9,5.5))
color = 'tab:blue'
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT] (%)')
ls1 = ax1.scatter(dfcloz["cluster_size"], dfcloz["resurgence_prob"], s=140, color="#2c7fb8", label='A.2.2')
ax1.plot(dfcloz["cluster_size"], dfcloz["resurgence_prob"], lw=0.5, color="#2c7fb8")

ls2 = ax1.scatter(dfcluk["cluster_size"], dfcluk["resurgence_prob"], s=140,color='#fd8d3c', label='B.1.1.7')
ax1.plot(dfcluk["cluster_size"], dfcluk["resurgence_prob"], lw=0.5, color='#fd8d3c')
ax1.set_xlim([0.5, 15])
ax1.set_ylim([0, 103])

# Labels for legend
lbs = [ls1, ls2]
labs = [l.get_label() for l in lbs]
ax1.legend(lbs, labs, loc=0, frameon=True)
ax1.annotate('C', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)

fig.tight_layout()
figure_folder = 'fig-files/'
cv.savefig(f"{figure_folder}/fig02_c_prob_sct_cluster_A22_vs_B117_numtests_{num_tests}.png", dpi=300)

plt.show()
