#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster", font_scale=1.1)

# Import data - x4 main scenarios 
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_ploz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_oz.csv')
df_pluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_uk.csv')

# Select one lvel of testing and one level of iq
num_tests = 6260
iq_factor = 0.5
cluster_size_th = 11
cluster_col = "cluster_size"
poisson_th = 1.1
poisson_col = "poisson_lambda"
which_outbreak_prob="resurgence_prob"
which_colourmap = "viridis"

def get_subframe(df, num_tests, column_name, col_th):
    df_sub = df[df["num_tests"] == num_tests]
    if column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[column_name] <=col_th) & (df_sub[column_name] >=0.5)]
    else:
        df_sub = df_sub[df_sub[column_name] <=col_th]

    df_sub = df_sub[["iq_factor", which_outbreak_prob, column_name]]
    df_map = df_sub.pivot("iq_factor", column_name, which_outbreak_prob)
    return df_map

def plot_heatmaps(df_map_list, fig_name_list, fig_labels=["A", "B"], xlabel='cluster size'):
    idx=0
    for df_map, fig_name in zip(df_map_list, fig_name_list):
        f, ax = plt.subplots(figsize=(14, 9))
        sns.heatmap(df_map, annot=True, fmt=".0f", linewidths=.5, ax=ax, cmap=which_colourmap, vmin=0, vmax=100, cbar_kws={'label': 'probabilty [%]'})
        ax.set_ylabel('Q/I leakage')
        ax.set_xlabel(xlabel)
        ax.annotate(fig_labels[idx], xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=50)
        idx+=1
        f.tight_layout()
        cv.savefig(fig_name, dpi=300)
    return


figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'

dfcloz_map = get_subframe(df_cloz, num_tests, cluster_col, cluster_size_th) 
dfcluk_map = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th) 

plot_heatmaps([dfcloz_map, dfcluk_map], [f"{figure_folder}/fig_prob_outbreak_oc_map_cluster_oz.png", f"{figure_folder}/fig_prob_outbreak_oc_map_cluster_uk.png"])

dfploz_map = get_subframe(df_ploz, num_tests, poisson_col, poisson_th) 
dfpluk_map = get_subframe(df_pluk, num_tests, poisson_col, poisson_th) 

#plot_heatmaps([dfploz_map, dfpluk_map], [f"{figure_folder}/fig_prob_outbreak_oc_map_poisson_oz.png", f"{figure_folder}/fig_prob_outbreak_oc_map_poisson_uk.png"], fig_labels=["C", "D"], xlabel='daily rate\nimported infections')

plt.show()
