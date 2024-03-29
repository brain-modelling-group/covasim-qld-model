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
df_clin = pd.read_csv('../../results/csv-data/outbreak_cluster_size_b16172.csv')


def get_subframe(df, num_tests, iq_factor):
    return df[(df["num_tests"] == num_tests) & (df["iq_factor"] == iq_factor)]

# Select one lvel of testing and one level of iq
num_tests = 8360
iq_factor = 0.5

dfcloz = get_subframe(df_cloz, num_tests, iq_factor)
dfcluk = get_subframe(df_cluk, num_tests, iq_factor)
dfclin = get_subframe(df_clin, num_tests, iq_factor)

fig, ax1 = plt.subplots(figsize=(9,5.5))
ax1.set_xlabel('cluster size')
ax1.set_ylabel('P[SCT] (%)')
#ls1 = ax1.scatter(dfcloz["cluster_size"], dfcloz["resurgence_prob"], s=140, color="#2c7fb8", label='A.2.2')
ls1 = ax1.scatter(dfcloz["cluster_size"], dfcloz["resurgence_prob"], s=140, color="#2c7fb8", label='ancestral')

ax1.plot(dfcloz["cluster_size"], dfcloz["resurgence_prob"], lw=0.5, color="#2c7fb8")

#ls2 = ax1.scatter(dfcluk["cluster_size"], dfcluk["resurgence_prob"], s=140,color='#fd8d3c', label='B.1.1.7')
ls2 = ax1.scatter(dfcluk["cluster_size"], dfcluk["resurgence_prob"], s=140,color='#fd8d3c', label='alpha')
ax1.plot(dfcluk["cluster_size"], dfcluk["resurgence_prob"], lw=0.5, color='#fd8d3c')

#ls3 = ax1.scatter(dfclin["cluster_size"], dfclin["resurgence_prob"], s=140,color='#984ea3', label='B.1.617.2')
ls3 = ax1.scatter(dfclin["cluster_size"], dfclin["resurgence_prob"], s=140,color='#984ea3', label='delta')

ax1.plot(dfclin["cluster_size"], dfclin["resurgence_prob"], lw=0.5, color='#984ea3')
ax1.set_xlim([0.5, 15])
ax1.set_ylim([0, 103])

# Labels for legend
lbs = [ls1, ls2, ls3]
labs = [l.get_label() for l in lbs]
ax1.legend(lbs, labs, loc=0, frameon=True)
ax1.annotate('A', xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)

fig.tight_layout()
figure_folder = 'fig-files/'
cv.savefig(f"{figure_folder}/fig03_a_prob_sct_cluster_A22_vs_B117_vs_B16172_numtests_{num_tests}.png", dpi=300)

plt.show()
