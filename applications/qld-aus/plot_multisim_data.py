#!/usr/bin/env python
# coding: utf-8
"""
Plot results from multisim objects
=======================================================


# author: Paula Sanz-Leon, QIMRB, January 2021
#         
"""

# Import sciencey libraries
import pandas as pd
import numpy as np

# Import graphics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
sns.set(style="white", context="talk")
#rs = np.random.RandomState(8)
# Import covasim's goodies
import covasim as cv
import covasim.misc as cvm
import sciris as sc
# Other goodies
import datetime # current date and time
now = datetime.datetime.now()
now_str = now.strftime("%Y-%m-%d_%H-%M-%S")


def get_simulated_data(key, sims, do_moving_average=False):
    
    ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)

    if do_moving_average:
       # Moving average over X days
       num_days = 3
       for idx in range(yarr.shape[0]):
            yarr[idx, :] = np.convolve(yarr[idx, :], np.ones((num_days, ))/num_days, mode='same')

    return yarr
    


def plot_multisim_vs_emp_data(sim_data, figname, do_moving_average=False):
    # Input data
    inputs_folder = 'inputs'
    input_data = 'qld_health_epi_data.csv'

    # Load data
    data = pd.read_csv("/".join((inputs_folder, input_data)), parse_dates=['date'])

    # Set date as index
    data.set_index('date', inplace=True)

    # Start graphics objects
    f, ax1 = plt.subplots(1, 1, figsize=(28/3, 18/3), sharex=True)

    # Plot new cases
    data_start_idx = cvm.day('2020-01-22', start_day='2020-01-22')
    data_end_idx = cvm.day('2020-05-31', start_day='2020-01-22')

    epi_data =  data['new_locally_acquired_cases'][data_start_idx:data_end_idx]
    
    if do_moving_average:
        num_days = 3
        epi_data = np.convolve(epi_data, np.ones((num_days, ))/num_days, mode='same')
    
    ax1.plot(data.index[data_start_idx:data_end_idx], epi_data, color='#e41a1c')
    # Set ticks every week
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator())
    # Set major ticks format
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.set_xlim([datetime.date(2020, 1, 22), datetime.date(2020, 5, 1)])
    ax1.set_ylabel('new cases')
    plt.setp(ax1.get_xticklabels(), 
             rotation=45, ha="right",
             rotation_mode="anchor")


    ax1.plot(data.index[data_start_idx:data_end_idx], np.percentile(sim_data, 50, axis=1), color='blue', alpha=1.0)
    ax1.plot(data.index[data_start_idx:data_end_idx], np.mean(sim_data, axis=1), color='green', alpha=1.0)
    ax1.plot(data.index[data_start_idx:data_end_idx], sim_data, color='black', alpha=0.3)

    cv.savefig(f'{figsfolder}/{figname}', dpi=100)
   
    plt.close()


if __name__ == '__main__':

    # Filepaths
    resultsfolder = 'results_recalibration_2020-01-15__2020-05-31-refined_betas'
    figsfolder = resultsfolder

    betas = np.arange(0.01, 0.03, 0.0005)
    seed_infections = np.arange(1, 26, 1)

    # Get all the data
    do_moving_average = False
    for beta_idx, this_beta in enumerate(betas):
        for infect_idx, this_infection in enumerate(seed_infections):
            # Generate file name
            this_file = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}.obj"
            msim = sc.loadobj(f'{resultsfolder}/{this_file}')
            sims = msim.sims
            sim_data = get_simulated_data('new_infectious', sims, do_moving_average=do_moving_average)[:, cvm.day('2020-01-22', start_day='2020-01-15'):cvm.day('2020-05-31', start_day='2020-01-15')].T
            
            if do_moving_average:
                figname = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}_moving_average.png"
            else:
                figname = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}.png"
            plot_multisim_vs_emp_data(sim_data, figname, do_moving_average=do_moving_average)
