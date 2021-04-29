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
num_tests = 8360
iq_factor = 1.0
cluster_size_th = 10
cluster_col = "cluster_size"
poisson_th = 1.0
poisson_col = "poisson_lambda"

def get_subframe(df, num_tests, par_column_name, col_th, day_column_name):
    df_sub = df[df["num_tests"] > 1000]
    if par_column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[par_column_name] <=col_th) & (df_sub[par_column_name] >=0.5) & (df_sub["iq_factor"] == iq_factor)]
    else:
        df_sub = df_sub[(df_sub[par_column_name] <=col_th) & (df_sub["iq_factor"] == iq_factor)]

    df_sub = df_sub[["num_tests", day_column_name, par_column_name]]
    df_map = df_sub.pivot("num_tests", par_column_name, day_column_name)
    return df_map

def plot_heatmaps(df_map_list, fig_name_list, xlab):

    for df_map, fig_name in zip(df_map_list, fig_name_list):
        f, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(df_map, annot=True, fmt=".0f", linewidths=.5, ax=ax, cmap="Reds", vmin=0, vmax=35)
        ax.set_ylabel('daily number of tests')
        ax.set_xlabel(xlab)
        f.tight_layout()
        cv.savefig(fig_name, dpi=300)
    return

dfcloz_fc_map = get_subframe(df_cloz, num_tests, cluster_col, cluster_size_th, "first_case_day_md") 
dfcluk_fc_map = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th, "first_case_day_md") 
dfploz_fc_map = get_subframe(df_ploz, num_tests, poisson_col, poisson_th, "first_case_day_md") 
dfpluk_fc_map = get_subframe(df_pluk, num_tests, poisson_col, poisson_th, "first_case_day_md") 

plot_heatmaps([dfcloz_fc_map, dfcluk_fc_map], [f"fig_fc_cluster_oz.png", "fig_fc_cluster_uk.png"], 'cluster size')
plot_heatmaps([dfploz_fc_map, dfpluk_fc_map], [f"fig_fc_poison_oz.png", "fig_fc_poisson_uk.png"], 'daily arrivals')


plt.show()
