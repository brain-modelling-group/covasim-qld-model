#!/usr/bin/env python
# coding: utf-8
"""
Use beta from calibrated model, multiplied by 1.7, which corresponds to the UK variant. 
We initialized the model on Feb 1st 2021 and run simulations until March 1st. 
UK variant.


# author: For QLD Paula Sanz-Leon, QIMRB, Aug 2020 - Feb 2021 
"""

# Import scientific python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pathlib as pathlib

# Import IDM/Optima code
import covasim as cv
import sciris as sc
import covasim_australia.utils as utils

# Add argument parser
import argparse

# Check covasim version is the one we actually need
cv.check_version('1.7.6', die=True)

parser = argparse.ArgumentParser()


parser.add_argument('--ncpus', default=8, 
                               type=int, 
                               help='''Maximum number of cpus used by MultiSim runs.''')

parser.add_argument('--results_path', default='results', 
                              type=str, 
                              help='''The relative and/or absolute path to the results folder, without the trailing /''')

parser.add_argument('--nruns', default=5, 
                               type=int, 
                               help='''Number of simulations to run per scenario. 
                                       Uses different PRNG seeds for each simulations.''')
parser.add_argument('--label', default='resurgence', 
                               type=str, 
                               help='''Label used in the output to tag which scenario
                                      we are running.''')
parser.add_argument('--dist', default='poisson', 
                              type=str, 
                              help='''Name of distribution to use to seed infections.
                                      Can be uniform, normal, etc''')
parser.add_argument('--par1', default=0.0, 
                              type=float, 
                              help=''' The "main" distribution parameter (e.g. mean).''')
  
parser.add_argument('--par2', default=0.0, 
                              type=float, 
                              help='''The "secondary" distribution parameter (e.g. std).''')

parser.add_argument('--cluster_size', 
                              default=0, 
                              type=int, 
                              help='''The number of infected people entering QLD community on a given date (default, 2020-10-01)''')

parser.add_argument('--global_beta', 
                              default=0.0112925463308101898, 
                              type=float, 
                              help='''Number of ppl infected at the beginning of the simulation.''')

parser.add_argument('--iq_factor', 
                              default=1.0, 
                              type=float, 
                              help='''Isolation and quarantine factors combined''')

parser.add_argument('--num_tests', 
                              default=6260, 
                              type=int, 
                              help='''Average number of tests per day. Value based on average over period 2021-01-14 to 2021-02-16. Std dev: 2100''')

parser.add_argument('--start_simulation_date', default='2021-02-01', 
                              type=str, 
                              help='''The date at which simulation starts.''')

parser.add_argument('--end_simulation_date', default='2021-03-15', 
                              type=str, 
                              help='''The date at which simulation finishes.''')

parser.add_argument('--epi_file', 
                              default='qld_epi_data_qld-health_calibration_2021-01-14_2021-02-16_raw.csv', 
                              type=str, 
                              help='''The name of the csv file with empirical data under inputs/.''')

parser.add_argument('--layer_betas_file', 
                              default='qld_model_layer_betas_02.csv', 
                              type=str, 
                              help='''The name of the csv file with layer-specific betas.''')

def define_beta_changes(betasfile, layers):

    beta_data  = pd.read_csv(betasfile, parse_dates=['date'])
    betas_interventions = []

    for this_layer in layers:
      # Load data for this layer
      beta_layer = np.array(beta_data[this_layer])
      # Find index of change, the date in which the change is implemented is the change index + 1
      change_idx = np.argwhere(beta_layer[0:-2]-beta_layer[1:-1]) + 1
      betas_interventions.append(cv.change_beta(days=['2020-01-01'] + [beta_data['date'][change_idx.flat[ii]] for ii in range(len(change_idx.flat))], 
                                                changes= [1.0] + [beta_data[this_layer][change_idx.flat[ii]] for ii in range(len(change_idx.flat))], 
                                                layers=[this_layer], do_plot=False))
    return betas_interventions

def make_sim(load_pop=True, popfile='qldppl.pop', datafile=None, agedatafile=None, input_args=None, betasfile=None):
    start_day = input_args.start_simulation_date
    iq_factor = input_args.iq_factor

    layers = ['H', 'S', 'W', 'C', 
              'church', 
              'pSport', 
              'cSport', 
              'entertainment', 
              'cafe_restaurant', 
              'pub_bar', 
              'transport', 
              'public_parks', 
              'large_events', 
              'social']   

    pars = {'pop_size': 200e3,    # Population size
            'pop_infected': 0, # input_args.init_seed_infections,   # Original population infedcted
            'pop_scale': 25.5,    # Population scales to 5.1M ppl in QLD
            'rescale': True,      # Population dynamics rescaling
            'rand_seed': 42,      # Random seed to use
            'rel_death_prob': 0.6,#
            'beta': input_args.global_beta, 
                                       # H        S       W       C   church   psport  csport    ent     cafe    pub     trans    park        event    soc
            'contacts':    pd.Series([4.0,    21.0,    5.0,    1.0,   20.0,   40.0,    30.0,    25.0,   19.00,  30.00,   25.00,   10.00,     50.00,   6.0], index=layers).to_dict(),
            'beta_layer':  pd.Series([1.0,     0.3,    0.2,    0.1,    0.04,   0.2,     0.1,     0.01,   0.04,   0.06,    0.16,    0.03,      0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([1.0, iq_factor/100.0, iq_factor/10.0, iq_factor/10.0, iq_factor/100.0, iq_factor/10.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0, iq_factor/10.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0], index=layers).to_dict(),
            'quar_factor': pd.Series([1.0, iq_factor/100.0, iq_factor/10.0, iq_factor/10.0, iq_factor/100.0, iq_factor/10.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0, iq_factor/10.0, iq_factor/100.0, iq_factor/100.0, iq_factor/100.0], index=layers).to_dict(),
            'n_imports': 0.0, # Number of new cases per day -- can be varied over time as part of the interventions
            'start_day': input_args.start_simulation_date,
            'end_day':   input_args.end_simulation_date,
            'verbose': 0}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    # Layer-specific betas    
    beta_ints = define_beta_changes(betasfile, layers)             
    sim.pars['interventions'].extend(beta_ints)

    # 
    ntpts = sim.day(input_args.end_simulation_date)-sim.day(input_args.start_simulation_date)
    sim.pars['interventions'].append(cv.test_num(daily_tests=[input_args.num_tests]*ntpts, 
                                                 start_day=input_args.start_simulation_date, 
                                                 end_day='2021-03-16', 
                                                 symp_test=100.0, test_delay=1))
    # Tracing
    trace_probs = {'H': 1.00, 'S': 0.95, 
                   'W': 0.80, 'C': 0.05, 
                   'church': 0.50, 
                   'pSport': 0.80, 
                   'cSport': 0.50,
                   'entertainment': 0.10, 
                   'cafe_restaurant': 0.70, 
                   'pub_bar': 0.50, 
                   'transport': 0.50, 
                   'public_parks': 0.00, 
                   'large_events': 0.05, 
                   'social': 0.90}
    trace_time = {'H': 1, 'S': 2, 
                  'W': 2, 'C': 14, 
                  'church': 5, 
                  'pSport': 3, 
                  'cSport': 3, 
                  'entertainment': 7,
                  'cafe_restaurant': 7, 
                  'pub_bar': 7, 
                  'transport': 14, 
                  'public_parks': 21,  
                  'large_events': 21,
                  'social': 3}


    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=trace_probs, 
                                                        trace_time=trace_time, 
                                                        start_day=0, do_plot=False))

    # Test cluster size ie, number of infections arriging at one on a given date
    sim.pars['interventions'].append(utils.SeedInfection({sim.day(input_args.start_simulation_date): input_args.cluster_size}))


    # Set 'Borders opening' interventions
    if input_args.label == 'cluster':
        # Test cluster size ie, number of infections arriging at one on a given date
        sim.pars['interventions'].append(utils.SeedInfection({sim.day(input_args.start_simulation_date): input_args.cluster_size}))

    if input_args.label == 'distributed':
        dist_kwd_arguments = {'dist': input_args.dist, 'par1': input_args.par1, 'par2': input_args.par2}
        seed_infection_dict  = utils.generate_seed_infection_dict(input_args.start_simulation_date, 
                                                                  input_args.start_simulation_date,
                                                                  input_args.end_simulation_date,
                                                                  **dist_kwd_arguments)

        sim.pars['interventions'].append(utils.SeedInfection(seed_infection_dict))



    sim.initialize()

    return sim

# Start setting up to run
# NB, this file assumes that you've already generated a population file saved in the same folder as this script, called qldpop.pop

if __name__ == '__main__':
    
    T = sc.tic()

    # Load argparse
    args = parser.parse_args()

    # Inputs
    inputsfolder = 'inputs'
    datafile = f'{inputsfolder}/{args.epi_file}'
    agedatafile = f'{inputsfolder}/qld_demo_data_abs.csv'
    populationfile = f'{inputsfolder}/qldppl.pop'
    betasfile = f'{inputsfolder}/{args.layer_betas_file}'

    # Results paths
    resultsfolder = args.results_path
    # simulation data path
    simfolder = f'{resultsfolder}/sim-data'
    # figures data path
    figfolder = f'{resultsfolder}/figures'

    pathlib.Path(simfolder).mkdir(parents=True, exist_ok=True)
    pathlib.Path(figfolder).mkdir(parents=True, exist_ok=True)

    # Create instance of simulator
    sim  = make_sim(load_pop=True, 
                    popfile=populationfile, 
                    datafile=datafile, 
                    agedatafile=agedatafile,
                    betasfile=betasfile,
                    input_args=args)

    # Do the stuff & save results
    msim = cv.MultiSim(base_sim=sim, par_args={'ncpus': args.ncpus})
    msim.run(n_runs=args.nruns, reseed=True, noise=2**-6)
    data = utils.get_ensemble_trace('new_diagnoses', msim.sims)
    idx_date = utils.detect_outbreak(data)


    if idx_date is not None:
      outbreak_data = {'outbreak': True}
    else
      outbreak_data = {'outbreak': False}

    df_data  = sc.mergedicts(outbreak_data, {'outbreak_day': idx_date, 'iq_factor': args.iq_factor/10.0})
    df = pd.DataFrame (data, columns = ['outbreak','outbreak_day','iq_factor'])

    
    # Plot all sims together 
    if args.label == 'cluster':
        msim_filename = f"{simfolder}/qld_{args.label}_{args.start_simulation_date}_{args.end_simulation_date}_iqf_{args.iq_factor/10.0:.{4}f}_{args.cluster_size:04d}"
        
    if args.label == 'distributed':
        msim_filename = f"{simfolder}/qld_{args.label}_{args.start_simulation_date}_{args.end_simulation_date}_iqf_{args.iq_factor/10.0:.{4}f}_{args.dist}_{args.par1:.{4}f}"

    msim.save(msim_filename+".obj")
    # Save basic results to csv
    df.to_csv(msim_filename+".csv")
    
    msim.reduce(quantiles={'low':0.01, 'high':0.99})
    msim_fig = msim.plot(do_show=False, scatter_args={'s': 8.0})
    msim_fig.savefig(msim_filename+'_msim_fig.png', dpi=100)
    plt.close('all')

    sc.toc(T)
        