#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=2.1)

# Import data - x4 main scenarios 
df_cloz = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')

# Select one lvel of testing and one level of iq
num_tests = 8360
cluster_size_th = 10
cluster_col = "cluster_size"
poisson_th = 1.0
poisson_col = "poisson_lambda"

def get_subframe(df, num_tests, par_column_name, col_th, day_column_name, iq_factor=0.1):
    df_sub = df[(df["num_tests"] > 1000) & (df["num_tests"] < 15000)]
    if par_column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[par_column_name] <=col_th) & (df_sub[par_column_name] >=0.5) & (df_sub["iq_factor"] == iq_factor)]
    else:
        df_sub = df_sub[(df_sub[par_column_name] <=col_th) & (df_sub["iq_factor"] == iq_factor)]

    df_sub = df_sub[["num_tests", day_column_name, par_column_name]]
    df_map = df_sub.pivot("num_tests", par_column_name, day_column_name)
    return df_map

def plot_heatmaps(df_map_list, fig_name_list, xlab, cmap_name='inferno', fig_label='A'):
    for df_map, fig_name in zip(df_map_list, fig_name_list):
        f, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(df_map, annot=True, fmt=".0f", linewidths=.5, ax=ax, cmap=cmap_name, vmin=0, vmax=100, cbar_kws={'label': 'probabilty [%]'})
        plt.yticks(rotation=0) 
        ax.set_ylabel('daily number of tests')
        ax.set_xlabel(xlab)
        ax.annotate(fig_label, xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=32)
        f.tight_layout()
        cv.savefig(fig_name, dpi=300)
    return

low_iq_factor = 0.1
dfcluk_fc_map_low_iq = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th, "resurgence_prob", iq_factor=low_iq_factor) 
high_iq_factor = 1.0
dfcluk_fc_map_high_iq = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th, "resurgence_prob", iq_factor=high_iq_factor) 

figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
plot_heatmaps([dfcluk_fc_map_low_iq,], [f"{figure_folder}/supfig06_a_prob_sct_vs_tests_cluster_b117_low_iq_0.1.png"], 'cluster size', cmap_name="viridis")
plot_heatmaps([dfcluk_fc_map_high_iq,], [f"{figure_folder}/supfig06_b_prob_sct_vs_tests_cluster_b117_high_iq_1.0.png"], 'cluster size', cmap_name="viridis", fig_label='B')

plt.show()
