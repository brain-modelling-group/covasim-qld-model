import sciris as sc
import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Filepaths
resultsfolder = 'results_recalibration'
figsfolder = resultsfolder

betas = np.arange(0.01, 0.03, 0.0005)
seed_infections = np.arange(1, 12, 1)


# Axes of PSE
num_betas = betas.shape[0]
num_infections = seed_infections.shape[0]
num_runs = 15


mismatch_arr = np.zeros((num_runs, num_betas, num_infections))

# Get all the data
for beta_idx, this_beta in enumerate(betas):
    for infect_idx, this_infection in enumerate(seed_infections):

        this_fit_file = f"qld_update_locally_acquired_recalibration_2020-01-15_2020-05-31_{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}_fit.obj"
        fitting_list = sc.loadobj(f'{resultsfolder}/{this_fit_file}')

        for fit_idx, this_fit in enumerate(fitting_list):
            mismatch_arr[fit_idx, beta_idx, infect_idx] = this_fit.mismatch 
        

fig, axs = plt.subplots(nrows=2, ncols=8, figsize=(9, 6),
                        subplot_kw={'xticks': [], 'yticks': []})


x = seed_infections
y = betas

axim = []
for ii in range(num_runs):
    im = axs.flat[ii].imshow(np.log10(mismatch_arr[ii, ...]), interpolation='none', origin='lower', extent = [0, 1, 0, 1])
    axim.append(im)

axs[1,6].set_xticks([0.0, 0.5, 1.0])
axs[1,6].set_xticklabels(["1", "6", "11"])
axs[1,6].set_yticks([0.0, 0.5, 1.0])
axs[1,6].set_yticklabels(["0.01", "0.015", "0.03"])
plt.xlabel('num seed infections')
plt.ylabel('beta')


for ax, im in zip(axs.flat[:-2], axim):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.02)
    plt.colorbar(im, cax=cax)

plt.show()