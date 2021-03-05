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
num_tests = 4160
iq_factor = 0.5
cluster_size_th = 18
cluster_col = "cluster_size"
poisson_th = 1.5
poisson_col = "poisson_lambda"

outbreak_cases = ['outbreak', 'under control']
column_names = ["outbreak_prob", "control_prob"]


def get_subframe(df, num_tests, column_name, col_th):
    df_sub = df[df["num_tests"] == num_tests]
    if column_name == "poisson_lambda":
        df_sub = df_sub[(df_sub[column_name] <=col_th) & (df_sub[column_name] >=0.5) & (df_sub["iq_factor"] == 0.5)]
    else:
  	    df_sub = df_sub[(df_sub[column_name] <=col_th) & (df_sub["iq_factor"] == 0.5)]
        
    return df_sub

def barplot_cl(df, category_names, column_names, label_name, ylab, fig_name):
    """
    """
    
    if label_name == "poisson_lambda":
    	labels = [f'{label:.4f}' for label in df[label_name]]
    else:
    	labels = [f'{label}' for label in df[label_name]]

    data = df[column_names].values
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('YlOrRd_r')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(18, 18))
    #ax.invert_yaxis()
    #ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max()+1)
    ax.set_ylim(0.5, df[label_name].values.max()+0.5)
    ax.set_ylabel(ylab)

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]+1
        starts = data_cum[:, i] - widths
        #import pdb; pdb.set_trace()
        ax.barh(df[label_name], widths, left=starts, height=0.95, label=colname, color=color)
        xcenters = starts + (widths-0.5) / 2
        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'black'
        for y, (x, c) in enumerate(zip(xcenters, widths+0.5)):
            ax.text(x, y+1, str(int(c-1.0)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', frameon=False)
    ax.set_xlabel("probabilty [%]")

    fig.tight_layout()
    cv.savefig(fig_name, dpi=300)
    return fig, ax


def barplot_pl(df, category_names, column_names, label_name, ylab, fig_name):
    """
    """
    
    if label_name == "poisson_lambda":
    	labels = [f'{label:.2f}' for label in df[label_name]]
    else:
    	labels = [f'{label}' for label in df[label_name]]

    data = df[column_names].values
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('YlOrRd_r')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(18, 18))
    #ax.invert_yaxis()
    #ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max()+1)
    #ax.set_ylim(0.2, 1.8)
    ax.set_ylabel(ylab)
    #import pdb; pdb.set_trace()
    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] -  data[:, i]
        #import pdb; pdb.set_trace()
        ax.barh(labels, widths, left=starts, height=0.95, label=colname, color=color)
        xcenters = starts + (widths-0.5) / 2
        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'black'
        for y, (x, c) in enumerate(zip(xcenters, widths+0.5)):
            ax.text(x, y, str(int(c)), ha='center', va='center',
                    color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', frameon=False)
    ax.set_xlabel("probabilty [%]")

    #fig.tight_layout()
    cv.savefig(fig_name, dpi=300)
    return fig, ax

dfcloz_sub = get_subframe(df_cloz, num_tests, cluster_col, cluster_size_th) 
dfcluk_sub = get_subframe(df_cluk, num_tests, cluster_col, cluster_size_th) 
barplot_cl(dfcloz_sub, outbreak_cases, column_names, "cluster_size", 'cluster size', "fig_prob_barh_cluster_oz.png")
barplot_cl(dfcluk_sub, outbreak_cases, column_names, "cluster_size", 'cluster size', "fig_prob_barh_cluster_uk.png")

dfploz_sub = get_subframe(df_ploz, num_tests, poisson_col, poisson_th) 
dfpluk_sub = get_subframe(df_pluk, num_tests, poisson_col, poisson_th) 

barplot_pl(dfploz_sub, outbreak_cases, column_names, "poisson_lambda", 'daily arrivals', "fig_prob_barh_poisson_oz.png")
barplot_pl(dfpluk_sub, outbreak_cases, column_names, "poisson_lambda", 'daily arrivals', "fig_prob_barh_poisson_uk.png")

plt.show()

