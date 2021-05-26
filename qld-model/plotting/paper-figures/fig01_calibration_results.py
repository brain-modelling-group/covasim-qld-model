#!/usr/bin/env python
# Import scientific python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import IDM/Optima code
import covasim as cv
import sciris as sc



calibration_results_folder = '/home/paula/Dropbox/COVID/simulated-data/pbs.14804351-calibration-results/sim-data'
calibration_results_filename = 'qld_recalibration_mav15_numtests_2020-03-01_2020-05-15_0.0113_142.obj'
figure_folder = '/home/paula/Work/Articles/coronavirus-qld-calibration/figures'
figure_filename = 'qld_recalibration_mav15_numtests_2020-03-01_2020-05-15_0.0113_142'
# Load MultiSim() object
msim = sc.loadobj(f'{calibration_results_folder}/{calibration_results_filename}')
msim.reduce(quantiles={'low':0.01, 'high':0.99})

msim_fig = msim.plot(do_show=False, show_args={'data':True, 'ticks':True, 'interventions':False, 'legend':True}, scatter_args={'s': 8.0})
msim_fig.axes[0].annotate('A', xy=(0.05, 0.95), xycoords='figure fraction', fontsize=18)
msim_fig.axes[1].annotate('B', xy=(0.05, 0.635), xycoords='figure fraction', fontsize=18)
msim_fig.axes[2].annotate('C', xy=(0.05, 0.32), xycoords='figure fraction', fontsize=18)
plt.show()
#msim_fig.savefig(f"{figure_folder}/{figure_filename}.png", dpi=300)