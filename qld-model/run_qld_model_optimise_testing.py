#!/usr/bin/env python
# coding: utf-8
"""
(RE)calibration of QLD model, using layer-specific betas from 
inputs/qld_model_layer_betas.csv

# author: For QLD Paula Sanz-Leon, QIMRB, Aug-Dec 2020
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
import optuna as op

import os
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

parser.add_argument('--nruns', default=3, 
                               type=int, 
                               help='''Number of simulations to run per scenario. 
                                       Uses different PRNG seeds for each simulations.''')
parser.add_argument('--label', default='recalibration', 
                               type=str, 
                               help='''Label used in the output to tag which scenario
                                      we are running.''')

parser.add_argument('--dist', default='poisson', 
                              type=str, 
                              help='''Name of distribution to use to seed infections.
                                      Can be uniform, normal, etc''')

parser.add_argument('--p1', default=1.0, 
                            type=float, 
                            help=''' Dummy parameter for paramter sweeps.''')
  
parser.add_argument('--p2', default=1.0, 
                            type=float, 
                            help='''Dummy parameter for paramter sweeps.''')

parser.add_argument('--p3', default=1.0, 
                            type=float, 
                            help='''Dummy parameter for paramter sweeps.''')

parser.add_argument('--par1', default=1.0, 
                              type=float, 
                              help=''' The "main" distribution parameter (e.g. mean).''')
  
parser.add_argument('--par2', default=1.0, 
                              type=float, 
                              help='''The "secondary" distribution parameter (e.g. std).''')

parser.add_argument('--cluster_size', 
                              default=0, 
                              type=int, 
                              help='''The number of infected people entering QLD community on a given date (default, 2020-10-01)''')

parser.add_argument('--new_tests_mode', 
                              default='raw', 
                              type=str, 
                              help='''The column of new tests to use: Can be 'raw' or 'conv'.''')

parser.add_argument('--init_seed_infections', 
                               default=185, 
                               type=int, 
                               help='''Number of ppl infected at the beginning of the simulation.''')

parser.add_argument('--global_beta', default=0.010, 
                               type=float, 
                               help='''Number of ppl infected at the beginning of the simulation.''')

parser.add_argument('--start_calibration_date', default='2020-03-01', 
                              type=str, 
                              help='''The date at which calibration starts (default, '2020-02-15').''')


parser.add_argument('--end_simulation_date', default='2020-05-15', 
                              type=str, 
                              help='''The date at which calibration finishes.''')

parser.add_argument('--end_calibration_date', default='2020-05-15', 
                              type=str, 
                              help='''The date at which calibration finishes.''')


parser.add_argument('--epi_calibration_file', 
                              default='qld_epi_data_qld-health_calibration_2020-02-15_2020-05-15_mav05.csv', 
                              type=str, 
                              help='''The name of the csv file with empirical data under inputs/.''')

parser.add_argument('--layer_betas_file', 
                              default='qld_model_layer_betas_01.csv', 
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

def make_sim(load_pop=True, popfile='qldppl.pop', datafile=None, agedatafile=None, input_args=None, betasfile=None, pars=None):
    start_day = input_args.start_calibration_date
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

    sim_pars = {'pop_size': 200e3,    # Population size
            'pop_infected': pars["seed_infections"],  # Original population infedcted
            'pop_scale': 25.5,    # Population scales to 5.1M ppl in QLD
            'rescale': True,      # Population dynamics rescaling
            'rand_seed': 42,      # Random seed to use
            'rel_death_prob': 0.6,#
            'beta': pars["global_beta"],  # Overall beta to use for calibration portion of the simulations
                                       # H        S       W       C   church   psport  csport    ent     cafe    pub     trans    park        event    soc
            'contacts':    pd.Series([4.0,    21.0,    5.0,    1.0,   20.0,   40.0,    30.0,    25.0,   19.00,  30.00,   25.00,   10.00,     50.00,   6.0], index=layers).to_dict(),
            'beta_layer':  pd.Series([1.0,     0.3,    0.2,    0.1,    0.04,   0.2,     0.1,     0.01,   0.04,   0.06,    0.16,    0.03,      0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([1.0,     0.01,   0.1,    0.1,    0.01,   0.0,     0.0,     0.01,   0.01,   0.01,    0.10,    0.0,       0.01,   0.0], index=layers).to_dict(),
            'quar_factor': pd.Series([1.0,     0.01,   0.1,    0.1,    0.01,   0.0,     0.0,     0.01,   0.01,   0.01,    0.10,    0.00,      0.01,   0.0], index=layers).to_dict(),
            'n_imports': 0.0, # Number of new cases per day -- can be varied over time as part of the interventions
            'start_day': input_args.start_calibration_date,
            'end_day':   input_args.end_simulation_date,
            'verbose': 0}

    sim = cv.Sim(pars=sim_pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    
    beta_ints = define_beta_changes(betasfile, layers)             
    sim.pars['interventions'].extend(beta_ints)

    # Testing interventions
    # Testing numbers
    # data = pd.read_csv(datafile, parse_dates=['date'])
    # if input_args.new_tests_mode == 'raw':
    #    this_column = 'new_tests_raw'
    # else:
    #    this_column = 'new_tests'
    # new_tests = data[this_column].to_list()
    # new_tests = new_tests[-sim.day(data['date'][0]):]

    # sim.pars['interventions'].append(cv.test_num(daily_tests=new_tests, symp_test=input_args.p1))

    # Testing, following NSW example
    #import pdb; pdb.set_trace()
    # print(pars["test_a"])
    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-01', 
                                                  end_day='2020-03-12', 
                                                  symp_prob=pars["prob_a"],
                                                  asymp_quar_prob=0.01, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-12', 
                                                  end_day='2020-03-19', 
                                                  symp_prob=pars["prob_b"],
                                                  asymp_quar_prob=0.01, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-19', 
                                                  end_day='2020-03-29', 
                                                  symp_prob=pars["prob_c"],
                                                  asymp_quar_prob=0.01, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-29', 
                                                  end_day='2020-05-15', 
                                                  symp_prob=pars["prob_lockdown"],
                                                  asymp_quar_prob=0.01, do_plot=False))


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

    # # Add known infections from Victoria and the cluster in the youth centre in brisbane
    # sim.pars['interventions'].append(utils.SeedInfection({sim.day('2020-07-29'): 2, sim.day('2020-08-22'): 9, sim.day('2020-09-09'): 9}))

    # # Test cluster size ie, number of infections arriging at one on a given date
    # sim.pars['interventions'].append(utils.SeedInfection({sim.day('2020-10-01'): args.cluster_size}))


    # Close borders, then open them again to account for victorian imports and leaky quarantine
    # sim.pars['interventions'].append(cv.dynamic_pars({'n_imports': {'days': [sim.day('2020-03-30'), 
    #                                                                          sim.day('2020-07-10'), 
    #                                                                          sim.day('2020-08-08'),
    #                                                                          sim.day('2020-09-23'),  # QLD/NSW Border population
    #                                                                          sim.day('2020-09-25')], # ACT
    #                                                                 'vals': [0.01, 0.5, 0.1, 0.12, 0.15]}}, do_plot=False))
    # sim.pars['interventions'].append(cv.dynamic_pars({'beta': {'days': [sim.day('2020-03-30'), sim.day('2020-09-30')], 
    #                                                            'vals': [0.01, 0.015]}}, do_plot=False))
    sim.initialize()

    return sim

def run_sim(pars):
    # Load argparse
    args = parser.parse_args()
    # Inputs
    inputsfolder = 'inputs'
    datafile = f'{inputsfolder}/{args.epi_calibration_file}'
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
                    input_args=args,
                    pars=pars)

    # Do the stuff & save results
    msim = cv.MultiSim(base_sim=sim, par_args={'ncpus': args.ncpus})
    msim.run(n_runs=args.nruns, reseed=True, noise=0)

   
    # Calculate fits 
    fit_pars_dict = {'absolute':True,
                     'use_median':True,
                     'font-size': 14}
    mismatch = 0.0
    for this_sim in msim.sims: 
        fit = this_sim.compute_fit(keys=['cum_diagnoses', 'cum_tests'],
                                         weights= [1.0, 1.0],
                                         **fit_pars_dict)
        mismatch += fit.mismatch

    # just average mismatch
    mismatch /= args.nruns
    return mismatch



def run_trial(trial):
    ''' Define the objective for Optuna '''
    pars = {}
    pars["global_beta"]  = trial.suggest_uniform('global_beta', 0.01, 0.011) # Sample from beta values within this range
    pars["seed_infections"]  = trial.suggest_int('seed_infections', 120, 200, 1) # Sample from beta values within this range
    pars["prob_a"] = trial.suggest_uniform('prob_a', 0.0, 0.01) # Sample from beta values within this range
    pars["prob_b"] = trial.suggest_uniform('prob_b', 0.05, 0.1) # Sample from beta values within this range
    pars["prob_c"] = trial.suggest_uniform('prob_c', 0.05, 0.2) # Sample from beta values within this range
    pars["prob_lockdown"] = trial.suggest_uniform('prob_lockdown', 0.05, 0.3) # Sample from beta values within this range

    mismatch = run_sim(pars)
    return mismatch


def make_study():
    ''' Make a study, deleting one if it already exists '''
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f'Removed existing calibration {db_name}')
    output = op.create_study(storage=storage, study_name=name)
    return output

def worker():
    ''' Run a single worker '''
    study = op.load_study(storage=storage, study_name=name)
    output = study.optimize(run_trial, n_trials=n_trials)
    return output

def run_workers():
    ''' Run multiple workers in parallel '''
    output = sc.parallelize(worker, n_workers)
    return output

if __name__ == '__main__':
    
     # Settings
    n_workers = 1 # Define how many workers to run in parallel
    n_trials = 100 # Define the number of trials, i.e. sim runs, per worker
    name      = 'my-example-calibration'
    db_name   = f'{name}.db'
    storage   = f'sqlite:///{db_name}'

    # Run the optimization
    tstart = sc.tic()
    make_study()
    worker()
    study = op.load_study(storage=storage, study_name=name)
    best_pars = study.best_params
    T = sc.toc(tstart, output=True)
    print(f'\n\nOutput: {best_pars}, time: {T:0.1f} s')


