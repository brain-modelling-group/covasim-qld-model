    #!/usr/bin/env python
# coding: utf-8
"""
Illustrate how to load simulation objects and data
=============================================================

# author: For QLD Paula Sanz-Leon, QIMRB, September 2020
"""


resultsfolder = 'results'

# Files produced with run_qld_wave_02.py
list_of_files = [ 'qld_calibration_2020-09-16.obj']



def get_array_data(sims, results_key):
	ys = []
    for this_sim in sims:
        ys.append(this_sim.results[key].values)
    yarr = np.array(ys)
    return yarr


# Load the data
for file_idx, this_file in enumerate(list_of_files):
    msim = sc.loadobj(f'{resultsfolder}/{this_file}')
    sims = msim.sims
    data[..., file_idx] = get_array_data(sims, 'new_diagnoses')
    # Do something with the data array 


