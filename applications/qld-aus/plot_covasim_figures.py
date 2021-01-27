import sciris as sc
import numpy as np
import matplotlib.pyplot as plt

# Filepaths
resultsfolder = 'results_recalibration'
figsfolder = resultsfolder

betas = np.arange(0.01, 0.03, 0.0005)
seed_infections = np.arange(1, 2, 1)


# Axes of PSE
num_betas = betas.shape[0]
num_infections = seed_infections.shape[0]

fit_pars_dict = {'absolute':True,
                 'use_median':True,
                 'font-size': 14}

# Get all the data
for beta_idx, this_beta in enumerate(betas):
    for infect_idx, this_infection in enumerate(seed_infections):
        # Generate file name
        this_sim_file = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}.obj"
        msim = sc.loadobj(f'{resultsfolder}/{this_sim_file}')
        
        msim.reduce()
        # Plot all sims together
        msim_fig = msim.plot(do_show=False)
        msim_fig_path = f"{resultsfolder}/qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{this_beta:.{4}f}_{this_infection:02d}_msim_fig.png"
        msim_fig.savefig(msim_fig_path, dpi=100)
        plt.close()

        # Calculate fits independentely
        fitting_list = []
        for this_sim in msim.sims: 
            fitting_list.append(this_sim.compute_fit(keys=['new_diagnoses', 'cum_diagnoses'],
                                       weights= [4.0, 2.0],
                                       **fit_pars_dict))
        # Save list of fits
        fits_path = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}_fit.obj"
        sc.saveobj(filename=fits_path, obj=fitting_list)
        fit_fig_path = f"{resultsfolder}/qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{this_beta:.{4}f}_{this_infection:02d}_fit_fig.png"
        fit_fig = fitting_list[0].plot(do_show=False)
        fit_fig[0].savefig(fit_fig_path, dpi=100)
        plt.close('all')
        
    