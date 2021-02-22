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
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

font = {'size'   : 14}
matplotlib.rc('font', **font)


# Add argument parser
import argparse


parser = argparse.ArgumentParser()


parser.add_argument('--results_path',
                              default = '/home/paula/Dropbox/COVID/simulated-data/pbs.14686578',
                              type=str, 
                              help='''The relative and/or absolute path to the folder with sims, figs etc, without the trailing /''')

parser.add_argument('--results_folder',
                              default = '/mismatch',
                              type=str, 
                              help='''The relative path to the results folder. Start with /''')

parser.add_argument('--filename', 
                               default='qld_recalibration_raw_numtests_2020-02-15_2020-05-15_mismatch_mismatch_ndg_cdg_cdh_w.npy',                               type=str, 
                               help=''' Name of the npy with file with results''')


parser.add_argument('--vmax_lin', default=100.0, 
                               type=float, 
                               help='''Maximum value to threshold map (linear range)''')

parser.add_argument('--vmax_log', default=3.0, 
                               type=float, 
                               help='''Maximum value to threshold map (log10)''')

parser.add_argument('--beta_step', default=0.0005, 
                               type=float, 
                               help='''''')

parser.add_argument('--beta_min', default=0.01, 
                               type=float, 
                               help='''''')

parser.add_argument('--beta_max', default=0.03, 
                               type=float, 
                               help='''''')

parser.add_argument('--seed_min', default=1.0, 
                               type=float, 
                               help='''''')

parser.add_argument('--seed_max', default=100.0, 
                               type=float, 
                               help='''''')

def plot_mismatch_maps(betas, seed_infections, mismatch_arr, vmax_log10= 2.0, vmax_lin = 100, figtitle='no-title'):

    fig, axs = plt.subplots(nrows=4, ncols=4, figsize=(15, 11),
                            subplot_kw={'xticks': [], 'yticks': []})

    fig.suptitle(figtitle)
    x = seed_infections
    y = betas

    axim = []
    # Display first four individual runs
    num_to_display = 4
    for ii in range(num_to_display):
        im = axs[0, ii].imshow(np.log10(mismatch_arr[ii, ...]), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
        axim.append(im)

    # Means and medians
    im10 = axs[1, 0].imshow(np.log10(np.mean(mismatch_arr, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im11 = axs[1, 1].imshow(np.log10(np.percentile(mismatch_arr, 50, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im12 = axs[1, 2].imshow(np.mean(mismatch_arr, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_lin)
    im13 = axs[1, 3].imshow(np.percentile(mismatch_arr, 50, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_lin)

    axim.append(im10)
    axim.append(im11)
    axim.append(im12)
    axim.append(im13)
    
    # standard deviations and 90%  percentile 
    im20 = axs[2, 0].imshow(np.log10(np.std(mismatch_arr, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im21 = axs[2, 1].imshow(np.log10(np.percentile(mismatch_arr, 90, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im22 = axs[2, 2].imshow(np.std(mismatch_arr, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])
    im23 = axs[2, 3].imshow(np.percentile(mismatch_arr, 90, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])


     # standard deviations and 90%  percentile 
    im30 = axs[3, 0].imshow(np.log10(np.std(mismatch_arr, axis=0)+np.mean(mismatch_arr, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im31 = axs[3, 1].imshow(np.log10(np.percentile(mismatch_arr, 90, axis=0)+np.percentile(mismatch_arr, 50, axis=0)), interpolation='none', origin='lower', extent = [0, 1, 0, 1], vmax=vmax_log10)
    im32 = axs[3, 2].imshow(np.std(mismatch_arr, axis=0)+np.mean(mismatch_arr, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])
    im33 = axs[3, 3].imshow(np.percentile(mismatch_arr, 90, axis=0)+np.percentile(mismatch_arr, 50, axis=0), interpolation='none', origin='lower', extent = [0, 1, 0, 1])

    axim.append(im20)
    axim.append(im21)
    axim.append(im22)
    axim.append(im23)

    axs[3,3].set_xticks([0.0, 0.5, 1.0])
    axs[3,3].set_yticks([0.0, 0.5, 1.0])

    axim.append(im30)
    axim.append(im31)
    axim.append(im32)
    axim.append(im33)

    axs[3,3].set_xticks([0.0, 0.5, 1.0])
    axs[3,3].set_yticks([0.0, 1.0])


    halfpoint_infections = ((seed_infections[-1] - seed_infections[0]) / 2.0)+seed_infections[0]
    halfpoint_betas = ((betas[-1] - betas[0]) / 2.0)+ betas[0]

    axs[3,3].set_xticklabels([str(seed_infections[0]), str(halfpoint_infections), str(seed_infections[-1])])
    axs[3,3].set_yticklabels(["0.0", "0.03"])
    plt.xlabel('num seed infections')
    plt.ylabel('beta')

    axs_titles = ['run 00', 'run 01', 'run 02', 'run 03', 
                  'log10(mean)', 'log10(median)', 'mean', 'median',
                  'log10(std)', 'log10(90-th percentile)', 'std', '90-th percentile',
                  'log10(std+mean)', 'log10(90-th percentile + median)', 'std+mean', '90-th percentile + median',]

    for idx, ax in enumerate(axs.flat):
        ax.set_title(axs_titles[idx])

    for ax, im in zip(axs.flat, axim):
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.02)
        plt.colorbar(im, cax=cax)

    arr = np.array(np.percentile(mismatch_arr, 90, axis=0)+np.percentile(mismatch_arr, 50, axis=0))
    ind = np.unravel_index(np.argmin(arr), arr.shape)
    print(ind)
    print(y[ind[0]])
    print(x[ind[1]])    
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    
    # Load argparse
    args = parser.parse_args()

    # Filepaths
    results_path = args.results_path
    results_folder = args.results_folder
    filename = args.filename
    figtitle = args.filename

    # Define ranges explored
    betas = np.arange(args.beta_min, args.beta_max+args.beta_step, args.beta_step)
    seed_infections = np.arange(args.seed_min, args.seed_max+1, 1)

    mismatch_arr = np.load(f'{results_path}{results_folder}/{filename}')
    plot_mismatch_maps(betas, seed_infections, mismatch_arr, vmax_lin = args.vmax_lin, vmax_log10=args.vmax_log,figtitle=figtitle)
