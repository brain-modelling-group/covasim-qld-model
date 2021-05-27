#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import covasim as cv

sns.set_context("paper", font_scale=1.5)


num_tests = [6260, 8360, 12560, 31460]

SCT_50_detection_prob = [25.2, 25.3, 26.7, 30.3]
SCT_50_cluster_size_lo = [1, 1, 1, 2]
SCT_50_cluster_size_hi = [2, 2, 2, 3]
SCT_50_av_days_to_first_detection = [20, 17, 14, 9]
SCT_50_sd_days_to_first_detection = [8, 8, 7, 5]

SCT_70_detection_prob = [40, 40, 44, 54]
SCT_70_cluster_size_lo = [1, 2, 2, 4]
SCT_70_cluster_size_hi = [2, 3, 3, 5]
SCT_70_av_days_to_first_detection = [17, 14, 13, 6]
SCT_70_sd_days_to_first_detection = [7, 7, 5, 3]

SCT_90_detection_prob = [68, 67, 67, 64]
SCT_90_cluster_size_lo = [4, 4, 5, 6]
SCT_90_cluster_size_hi = [5, 5, 6, 7]
SCT_90_av_days_to_first_detection = [11, 7, 6, 4]
SCT_90_sd_days_to_first_detection = [5, 3, 3, 1]


fig, ax1 = plt.subplots(figsize=(9,5.5))
ax1.set_xlabel('number of daily tests')
ax1.set_ylabel('days until \nfirst confirmed case')
ax1.set_xscale('log')
ax1.set_xlim([6000, 33000])
ax1.set_ylim([0, 30])

ls1 = []    
ls1.append(ax1.fill_between(num_tests, np.array(SCT_50_av_days_to_first_detection)+np.array(SCT_50_sd_days_to_first_detection), 
                                       y2=np.array(SCT_50_av_days_to_first_detection)-np.array(SCT_50_sd_days_to_first_detection), facecolor="#fed976", alpha=0.6))

ls1.append(ax1.fill_between([6000, 6260], [np.array(SCT_50_av_days_to_first_detection[0])+np.array(SCT_50_sd_days_to_first_detection[0]), np.array(SCT_50_av_days_to_first_detection[0])+np.array(SCT_50_sd_days_to_first_detection[0])], 
                                       y2=[np.array(SCT_50_av_days_to_first_detection[0])-np.array(SCT_50_sd_days_to_first_detection[0]), np.array(SCT_50_av_days_to_first_detection[0])-np.array(SCT_50_sd_days_to_first_detection[0])], facecolor="#fed976", alpha=0.6))

ls1.append(ax1.fill_between([31460, 33000], [np.array(SCT_50_av_days_to_first_detection[-1])+np.array(SCT_50_sd_days_to_first_detection[-1]), np.array(SCT_50_av_days_to_first_detection[-1])+np.array(SCT_50_sd_days_to_first_detection[-1])], 
                                       y2=[np.array(SCT_50_av_days_to_first_detection[-1])-np.array(SCT_50_sd_days_to_first_detection[-1]), np.array(SCT_50_av_days_to_first_detection[-1])-np.array(SCT_50_sd_days_to_first_detection[-1])], facecolor="#fed976", alpha=0.6))

ls1.append(ax1.fill_between(num_tests, np.array(SCT_70_av_days_to_first_detection)+np.array(SCT_70_sd_days_to_first_detection), 
                                       y2=np.array(SCT_70_av_days_to_first_detection)-np.array(SCT_70_sd_days_to_first_detection), facecolor="#fc4e2a", alpha=0.2))

ls1.append(ax1.fill_between([6000, 6260], [np.array(SCT_70_av_days_to_first_detection[0])+np.array(SCT_70_sd_days_to_first_detection[0]), np.array(SCT_70_av_days_to_first_detection[0])+np.array(SCT_70_sd_days_to_first_detection[0])], 
                                       y2=[np.array(SCT_70_av_days_to_first_detection[0])-np.array(SCT_70_sd_days_to_first_detection[0]), np.array(SCT_70_av_days_to_first_detection[0])-np.array(SCT_70_sd_days_to_first_detection[0])], facecolor="#fc4e2a", alpha=0.2))

ls1.append(ax1.fill_between([31460, 33000], [np.array(SCT_70_av_days_to_first_detection[-1])+np.array(SCT_70_sd_days_to_first_detection[-1]), np.array(SCT_70_av_days_to_first_detection[-1])+np.array(SCT_70_sd_days_to_first_detection[-1])], 
                                       y2=[np.array(SCT_70_av_days_to_first_detection[-1])-np.array(SCT_70_sd_days_to_first_detection[-1]), np.array(SCT_70_av_days_to_first_detection[-1])-np.array(SCT_70_sd_days_to_first_detection[-1])], facecolor="#fc4e2a", alpha=0.2))


ls1.append(ax1.fill_between(num_tests, np.array(SCT_90_av_days_to_first_detection)+np.array(SCT_90_sd_days_to_first_detection), 
                                       y2=np.array(SCT_90_av_days_to_first_detection)-np.array(SCT_90_sd_days_to_first_detection), facecolor="#b10026", alpha=0.3))

ls1.append(ax1.fill_between([6000, 6260], [np.array(SCT_90_av_days_to_first_detection[0])+np.array(SCT_90_sd_days_to_first_detection[0]), np.array(SCT_90_av_days_to_first_detection[0])+np.array(SCT_90_sd_days_to_first_detection[0])], 
                                       y2=[np.array(SCT_90_av_days_to_first_detection[0])-np.array(SCT_90_sd_days_to_first_detection[0]), np.array(SCT_90_av_days_to_first_detection[0])-np.array(SCT_90_sd_days_to_first_detection[0])], facecolor="#b10026", alpha=0.3))

ls1.append(ax1.fill_between([31460, 33000], [np.array(SCT_90_av_days_to_first_detection[-1])+np.array(SCT_90_sd_days_to_first_detection[-1]), np.array(SCT_90_av_days_to_first_detection[-1])+np.array(SCT_90_sd_days_to_first_detection[-1])], 
                                       y2=[np.array(SCT_90_av_days_to_first_detection[-1])-np.array(SCT_90_sd_days_to_first_detection[-1]), np.array(SCT_90_av_days_to_first_detection[-1])-np.array(SCT_90_sd_days_to_first_detection[-1])], facecolor="#b10026", alpha=0.3))



ls1.append(ax1.plot(num_tests, np.array(SCT_50_av_days_to_first_detection), lw=4, color="black", zorder=1))
ls1.append(ax1.plot(num_tests, np.array(SCT_50_av_days_to_first_detection), lw=3, color="#fed976", zorder=1))
ls1.append(ax1.scatter(num_tests, SCT_50_av_days_to_first_detection, facecolor="#fed976", s=np.array(SCT_50_cluster_size_hi)*100, edgecolor='black', alpha=1.0, zorder=2))    

ls1.append(ax1.plot(num_tests, np.array(SCT_70_av_days_to_first_detection), lw=4, color="black", zorder=1, alpha=0.5))
ls1.append(ax1.plot(num_tests, np.array(SCT_70_av_days_to_first_detection), lw=3, color="#fc4e2a", zorder=1))
ls1.append(ax1.scatter(num_tests, SCT_70_av_days_to_first_detection, facecolor="#fc4e2a", s=np.array(SCT_70_cluster_size_hi)*100, edgecolor='black', alpha=1.0, zorder=2))

ls1.append(ax1.plot(num_tests, np.array(SCT_90_av_days_to_first_detection), lw=4, color="black", zorder=1, alpha=0.5))
ls1.append(ax1.plot(num_tests, np.array(SCT_90_av_days_to_first_detection), lw=3, color="#b10026", zorder=1))    
ls1.append(ax1.scatter(num_tests, SCT_90_av_days_to_first_detection, s=np.array(SCT_90_cluster_size_hi)*100, facecolor="#b10026",edgecolor='black', alpha=1.0, zorder=2))    


ax1.annotate("B", xy=(0.02, 0.9125), xycoords='figure fraction', fontsize=22)


ax1.annotate(
    'P[SCT]=90%', color='white', weight='bold',
    xy=(23000., 27), xycoords='data',
    xytext=(0, 0), textcoords='offset points',
    bbox=dict(boxstyle="round", fc="#b10026", ec="#b10026", alpha=1.0), 
    fontsize=12)

ax1.annotate(
    'P[SCT]=70%', color='white', weight='bold',
    xy=(23000., 24), xycoords='data',
    xytext=(0, 0), textcoords='offset points',
    bbox=dict(boxstyle="round", fc="#fc4e2a", ec="#fc4e2a", alpha=1.0),
    fontsize=12)

ax1.annotate(
    'P[SCT]=50%', weight='bold',
    xy=(23000., 21), xycoords='data',
    xytext=(0, 0), textcoords='offset points',
    bbox=dict(boxstyle="round", fc="#fed976", ec="#fed976", alpha=1.0),
    fontsize=12)

ax1.annotate(
    'estimated cluster size',
    xy=(8000, 27), xycoords='data',
    xytext=(-40, 0), textcoords='offset points', fontsize=14)

ax1.scatter([12500, 13750, 15500], [27.5, 27.5, 27.5], color=[0.5, 0.5, 0.5], s=np.array([3, 5, 7])*100)    
ax1.text(12350, 27, '3', color='white', weight='bold', fontsize=12)
ax1.text(13550, 27, '5', color='white', weight='bold', fontsize=12)
ax1.text(15350, 27, '7', color='white', weight='bold', fontsize=12)

# Labels for legend
#handler1, label1 = ax1.get_legend_handles_labels()
#ax1.legend(handler1, label1, loc="upper right", frameon=True)
fig.tight_layout()
figure_folder = '/home/paula/data_ext4/Dropbox/COVID/articles/coronavirus-qld-calibration/figures'
cv.savefig(f"{figure_folder}/fig03_d_prob_sct_cluster_tests_iq_0.1_uk-oz.png", dpi=300)

plt.show()
