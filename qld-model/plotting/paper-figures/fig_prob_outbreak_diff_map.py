#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster")

# Import data - x4 main scenarios 
df_cloz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
df_ploz = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_oz.csv')
df_pluk = pd.read_csv('/home/paula/data_ext4/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_uk.csv')

# Select one lvel of testing and one level of iq
num_tests = 6260
iq_factor = 1.0
cluster_size_th = 15
cluster_col = "cluster_size"
poisson_th = 1.3
poisson_col = "poisson_lambda"

def get_subframe(df, num_tests, column_name, col_th):
    df_sub = df[df["num_tests"] == num_tests]
    if column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[column_name] <=col_th) & (df_sub[column_name] >=0.5)]
    else:
        df_sub = df_sub[df_sub[column_name] <=col_th]

    df_inf = df_sub[["iq_factor", "outbreak_inf_prob", column_name]]
    df_inf = df_inf.pivot("iq_factor", column_name, "outbreak_inf_prob")

    df_cas = df_sub[["iq_factor", "outbreak_prob", column_name]]
    df_cas = df_cas.pivot("iq_factor", column_name, "outbreak_prob")

    return df_inf-df_cas

def plot_heatmaps(df_map_list, fig_name_list, xlab):

    for df_map, fig_name in zip(df_map_list, fig_name_list):
        f, ax = plt.subplots(figsize=(14, 9))
        sns.heatmap(df_map, annot=True, fmt=".0f", linewidths=.5, ax=ax, cmap="YlGnBu", vmin=0, vmax=24)
        ax.set_ylabel('quarantine/isolation factor')
        ax.set_xlabel(xlab)
        f.tight_layout()
        cv.savefig(fig_name, dpi=300)
    return

dfcloz_map = get_subframe(df_cloz, num_tests, cluster_col, cluster_size_th) 
dfcluk_map = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th) 

plot_heatmaps([dfcloz_map, dfcluk_map], ["fig_prob_resurgence_outbreak_diff_map_cluster_oz.png", "fig_prob_resurgence_outbreak_diff_map_cluster_uk.png"], 'cluster size')

dfploz_map = get_subframe(df_ploz, num_tests, poisson_col, poisson_th) 
dfpluk_map = get_subframe(df_pluk, num_tests, poisson_col, poisson_th) 

plot_heatmaps([dfploz_map, dfpluk_map], ["fig_prob_resurgence_outbreak_diff_map_poisson_oz.png", "fig_prob_resurgence_outbreak_diff_map_poisson_uk.png"], 'daily arrivals infections')

plt.show()
