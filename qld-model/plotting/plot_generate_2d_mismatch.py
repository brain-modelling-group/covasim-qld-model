#!/usr/bin/env python
# coding: utf-8
"""
Plot mismatch maps 
===================

# author: For QLD Paula Sanz-Leon, QIMRB, January 2021
"""

# Load the usuals
import sciris as sc
import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def plot_mismatch_maps(betas, seed_infections, mismatch_arr, vmax_log10= 2.0, vamx_lin = 100, figtitle):

    fig, axs = plt.subplots(nrows=3, ncols=4, figsize=(9, 6),
                            subplot_kw={'xticks': [], 'yticks': []})

    fig.suptitle(figtitle)
    x = seed_infections
    y = betas

    axim = []
    # Display first four individual runs
    num_to_display = 4
    for ii in range(num_to_display):
        im = axs.flat[0, ii].imshow(np.log10(mismatch_arr[ii, ...]), interpolation='none', origin='lower', extent = [0, 1, 0, 1])
        axim.append(im)

    # Means and medians
    im10 = axs[1, 0].imshow(np.log10(np.mean(mismatch_arr, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im11 = axs[1, 1].imshow(np.log10(np.percentile(mismatch_arr, 50, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im12 = axs[1, 2].imshow(np.mean(mismatch_arr, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vamax=vmax_lin)
    im13 = axs[1, 3].imshow(np.percentile(mismatch_arr, 50, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax_lin)

    axim.append(im10)
    axim.append(im11)
    axim.append(im12)
    axim.append(im13)
    
    # standard deviations and 90%  percentile 
    im20 = axs[2, 0].imshow(np.log10(np.std(mismatch_arr, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im21 = axs[2, 1].imshow(np.log10(np.percentile(mismatch_arr, 90, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im22 = axs[2, 2].imshow(np.std(mismatch_arr, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])
    im23 = axs[2, 3].imshow(np.percentile(mismatch_arr, 90, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])

    axim.append(im20)
    axim.append(im21)
    axim.append(im22)
    axim.append(im23)

    axs[2,3].set_xticks([0.0, 0.5, 1.0])
    axs[2,3].set_yticks([0.0, 0.5, 1.0])


    halfpoint_infections = (seed_infections[-1] - seed_infections[0]) / 2.0
    halfpoint_betas = (betas[-1] - betas[0]) / 2.0


    axs[2,3].set_xticklabels([str(seed_infections[0]), str(halfpoint_infections), str(seed_infections[-1])])
    axs[2,3].set_yticklabels([str(betas[0]), str(halfpoint_betas), str(betas[-1])])
    plt.xlabel('num seed infections')
    plt.ylabel('beta')


    for ax, im in zip(axs.flat, axim):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.02)
        plt.colorbar(im, cax=cax)

    plt.show()

if __name__ == '__main__':
    # Filepaths
    results_path = '/home/paula/data_ext4/Dropbox/COVID/simulated-data/pbs.14678514'
    results_folder = '/mismatch'
    filename = 'qld_recalibration_mav_numtests_2020-02-15_2020-04-10_mismatch_fit_ndg_cdg_cdh_w.npy'
    figtitle = 'mismatch_fit_ndg_cdg_cdh_w'

    betas = np.arange(0.01, 0.03, 0.0005)
    seed_infections = np.arange(1, 50, 1)


    # Axes of PSE
    num_betas = betas.shape[0]
    num_infections = seed_infections.shape[0]
    num_runs = 4