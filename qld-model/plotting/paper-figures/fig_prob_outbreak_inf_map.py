#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("poster")

# Import data - x4 main scenarios 
#data_folder = '/home/paula/data_ext4'
data_folder = '/home/paula'
#df_cloz = pd.read_csv(f'{data_folder}/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_oz.csv')
df_cluk = pd.read_csv(f'{data_folder}/Dropbox/COVID/simulated-data/resurgence/outbreak_cluster_size_uk.csv')
#df_ploz = pd.read_csv(f'{data_folder}/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_oz.csv')
df_pluk = pd.read_csv(f'{data_folder}/Dropbox/COVID/simulated-data/resurgence/outbreak_poisson_lambda_uk.csv')


# Select one lvel of testing and one level of iq
num_tests = 6260
iq_factor = 0.5
cluster_size_th = 15
cluster_col = "cluster_size"
poisson_th = 1.3
poisson_col = "poisson_lambda"

def get_subframe(df, iq_factor, column_name, col_th):
    df_sub = df[df["iq_factor"] == iq_factor]
    if column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[column_name] <=col_th) & (df_sub[column_name] >=0.5)]
    else:
        df_sub = df_sub[df_sub[column_name] <=col_th]

    df_sub_inf = df_sub[["num_tests", "outbreak_inf_prob", column_name]]
    df_sub_case = df_sub[["num_tests", "outbreak_prob", column_name]]
    #df_map = df_sub_inf.pivot("num_tests", column_name, "outbreak_prob")

    #import pdb; pdb.set_trace()
    df_map = df_sub_inf.pivot("num_tests", column_name, "outbreak_inf_prob") - df_sub_case.pivot("num_tests", column_name, "outbreak_prob")
    return df_map

def plot_heatmaps(df_map_list, fig_name_list, xlab):

    for df_map, fig_name in zip(df_map_list, fig_name_list):
        f, ax = plt.subplots(figsize=(14, 9))
        sns.heatmap(df_map, annot=True, fmt=".0f", linewidths=.5, ax=ax, cmap="YlGnBu_r", vmin=0, vmax=30)
        ax.set_ylabel('daily tests')
        ax.set_xlabel(xlab)
        f.tight_layout()
        cv.savefig(fig_name, dpi=300)
    return

#dfcloz_map = get_subframe(df_cloz, iq_factor, cluster_col, cluster_size_th) 
dfcluk_map = get_subframe(df_cluk, iq_factor, cluster_col, cluster_size_th) 


plot_heatmaps([dfcluk_map], ["fig_prob_outbreak_diff_map_cluster_uk_iq_0.5.png"], 'cluster size')

#dfploz_map = get_subframe(df_ploz, iq_factor, poisson_col, poisson_th) 
dfpluk_map = get_subframe(df_pluk, iq_factor, poisson_col, poisson_th) 

plot_heatmaps([dfpluk_map], ["fig_prob_outbreak_diff_map_poisson_uk_iq_0.5.png"], 'daily arrivals infections')

plt.show()
