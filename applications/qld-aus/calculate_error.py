#!/usr/bin/env python
# coding: utf-8
"""
Calculate error in QLD model 
=============================================================
"""

import numpy as np
import sciris as sc
import pandas as pd



def get_simulated_data(sims, key, av_days=3, low_q=25, high_q=75):
    """
    sims: a MultiSim object
    key: string with the key of the data we will use
    """
    ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)

    # Moving average over X-days
    num_days = av_days
    for idx in range(yarr.shape[0]):
        yarr[idx, :] = np.convolve(yarr[idx, :], np.ones((num_days, ))/num_days, mode='same')

    low_percentile  = np.percentile(yarr, low_q, axis=0)
    high_percentile = np.percentile(yarr, high_q, axis=0)
    halfsies = np.percentile(yarr, 50, axis=0)

    #import pdb; pdb.set_trace()
    return halfsies


if __name__ == '__main__':

    # Filepaths
    resultsfolder = 'results_recalibration'
    figsfolder = 'figs'

    betas = np.arange(0.01, 0.04, 0.0005)
    seed_infections = np.arange(1, 2, 1)


    # Axes of PSE
    num_betas = betas.shape[0]
    num_infections = seed_infections.shape[0]

    # Save result of PSE
    error_matrix = np.zeros((num_betas, num_infections))

    # Load the simulated data
    sim_length_days = 122

    data_arr = np.zeros((sim_length_days, num_betas, num_infections))

    # Get all the data
    for beta_idx, this_beta in enumerate(betas):
        for infect_idx, this_infection in enumerate(seed_infections):
            # Generate file name
            this_file = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-15_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}.obj"
            msim = sc.loadobj(f'{resultsfolder}/{this_file}')
            sims = msim.sims
            data_arr[..., beta_idx, infect_idx] = get_simulated_data(sims, 'new_diagnoses')



    # Load empirical data
    inputs_folder = 'inputs'
    input_data = 'qld_health_epi_data.csv'

    # Load data
    data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

    # Get 
    start_sim_idx = sims[0].day('2020-01-22') # First data point of sim data is 15-01-2020
    end_sim_idx   = sims[0].day('2020-05-15') # Last data point of simulated data is 15-05-2020 

    start_data_idx = 0 # First data point of sim data is 22-01-2020
    end_data_idx   = sims[0].day('2020-05-15')-start_sim_idx # Last data point of empirical data is today

    xx = data['new_locally_acquired_cases'][start_data_idx:end_data_idx]
    num_days = 3
    xx = np.convolve(xx, np.ones((num_days, ))/num_days, mode='same')
    # error distribution between empirical data and median prediction
    # [num par values, timepoints]
    yy = np.abs(data_arr[start_sim_idx:end_sim_idx, ...]-xx[:, np.newaxis, np.newaxis])

    # Get percentiles of the error distribution 
    yy_med = np.percentile(yy, q=50, axis=0)
    yy_q1  = np.percentile(yy, q=25, axis=0)
    yy_q3  = np.percentile(yy, q=75, axis=0)

    np.savez("recalibration_2d_pse", res=yy, x=seed_infections, y=betas)

    import pdb; pdb.set_trace()
