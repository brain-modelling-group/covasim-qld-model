#!/usr/bin/env python
# coding: utf-8
"""
Collate mismatch values from batches of simulations. 
Save results in numpy arrays. 

=====================================================

# author: Paula Sanz-Leon, QIMRB, February 2021
"""


# Filepaths

def collate_mismatch_results_list(betas, seed_infections, file_string):
    """
    Load fit objects into an array. It expects that the obj file have a list with 
    as many elements as num_runs. 

    Returns dict with a single array of shape (num_runs, num_betas, num_infections)
    """

    # Check the first file to get the number of runs
    this_fit_file = f"{file_string}{betas[0]:.{4}f}_{seed_infections[0]:02d}_fit.obj"
    fitting_list = sc.loadobj(f'{resultsfolder}/{this_fit_file}')

    num_runs = len(fitting_list)
    # Axes of PSE
    num_betas = betas.shape[0]
    num_infections = seed_infections.shape[0]

    # 
    mismatch_arr = np.zeros((num_runs, num_betas, num_infections))

    # Get all the data
    for beta_idx, this_beta in enumerate(betas):
        for infect_idx, this_infection in enumerate(seed_infections):

            this_fit_file = f"{file_string}{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}_fit.obj"
            try:
                fitting_list = sc.loadobj(f'{resultsfolder}/{this_fit_file}')
            except:
                print(f'{resultsfolder}/{this_fit_file}' '~not found~')
                fitting_list = [np.nan]*num_runs
            
            for fit_idx, this_fit in enumerate(fitting_list):
                mismatch_arr[fit_idx, beta_idx, infect_idx] = this_fit.mismatch         

   output_dict = {'mismatch_ndg_cdg_cdh_w': mismatch_arr}
   return output_dict



def collate_mismatch_results_dict(betas, seed_infections, file_string, resultsfolder):
    """
    Load fit objects into an array. It expects that the obj file to have a
    dict with the mismatch results using different combinations of
    observables. Each value in the dict is a list with as many elements as
    num_runs. 

    # Input dict
    fitting_dict = {'fit_ndg_cdg_cdh_w': [], 
                    'fit_ndg_cdg_cdh_u': [], 
                    'fit_ndg': [], 
                    'fit_cdg': [], 
                    'fit_cdh': []}

    Returns
    A dictionary with the same keys as the input dictionary, but each value element is a np.array 
    of shape (num_runs, num_betas, num_infections)
    """
    # Axes of PSE
    num_betas = betas.shape[0]
    num_infections = seed_infections.shape[0]

    # Get number of runs using the firs fitting list 
    num_runs = len(fitting_dict[fitting_dict.keys()[0]])

    # Check the first file to get basic info for output
    this_fit_file = f"{file_string}{betas[0]:.{4}f}_{seed_infections[0]:02d}_fit.obj"
    fitting_dict = sc.loadobj(f'{resultsfolder}/{this_fit_file}')
    
    # Create output dictionary with the same keys as input dictionary
    output_dict = {x:np.zeros((num_runs, num_betas, num_infections)) for x in fitting_dict.keys()}

    # Get all the data
    for beta_idx, this_beta in enumerate(betas):
        for infect_idx, this_infection in enumerate(seed_infections):

            this_fit_file = f"{file_string}{betas[beta_idx]:.{4}f}_{seed_infections[infect_idx]:02d}_fit.obj"
            fitting_dict = sc.loadobj(f'{resultsfolder}/{this_fit_file}')

            for key in fitting_dict.keys():
                fitting_list = fitting_dict[key]

                for fit_idx, this_fit in enumerate(fitting_list):
                    mismatch_arr[fit_idx, beta_idx, infect_idx] = this_fit.mismatch 

   return output_dict


if __name__ == '__main__':

resultsfolder = '/home/paula/Work/Code/Python/covasim-australia-qld/applications/qld-aus/results_recalibration_2020-02-15_2020-05-15-local-cases/sim-data'
file_string = 'qld_recalibration_raw_numtests_2020-02-15_2020-05-15_'

# Define ranges explored
betas = np.arange(0.01, 0.03, 0.0005)
seed_infections = np.arange(1, 50, 1)


