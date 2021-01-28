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

# Add argument parser
import argparse

plt.ioff()

# Check covasim version is the one we actually need
cv.check_version('1.7.6', die=True)

parser = argparse.ArgumentParser()


parser.add_argument('--results_path', default='results', 
                              type=str, 
                              help='''The relative and/or absolute path to the results folder, without the trailing /''')

parser.add_argument('--nruns', default=5, 
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
                               default=50, 
                               type=int, 
                               help='''Number of ppl infected at the beginning of the simulation.''')

parser.add_argument('--global_beta', default=0.015, 
                               type=float, 
                               help='''Number of ppl infected at the beginning of the simulation.''')


parser.add_argument('--start_calibration_date', default='2020-02-15', 
                              type=str, 
                              help='''The date at which calibration starts (default, '2020-02-15').''')

parser.add_argument('--end_calibration_date', default='2020-05-15', 
                              type=str, 
                              help='''The date at which calibration finishes (default, '2020-06-30').''')


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

    pars = {'pop_size': 200e3,    # Population size
            'pop_infected': input_args.init_seed_infections,   # Original population infedcted
            'pop_scale': 25.5,    # Population scales to 5.1M ppl in QLD
            'rescale': True,      # Population dynamics rescaling
            'rand_seed': 42,      # Random seed to use
            'rel_death_prob': 0.6,#
            'beta': input_args.global_beta,  # Overall beta to use for calibration portion of the simulations
                                       # H        S       W       C   church   psport  csport    ent     cafe    pub     trans    park        event    soc
            'contacts':    pd.Series([4.0,    21.0,    5.0,    1.0,   20.0,   40.0,    30.0,    25.0,   19.00,  30.00,   25.00,   10.00,     50.00,   6.0], index=layers).to_dict(),
            'beta_layer':  pd.Series([1.0,     0.3,    0.2,    0.1,    0.04,   0.2,     0.1,     0.01,   0.04,   0.06,    0.16,    0.03,      0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([1.0,     0.01,   0.1,    0.1,    0.01,   0.0,     0.0,     0.01,   0.01,   0.01,    0.10,    0.0,       0.01,   0.0], index=layers).to_dict(),
            'quar_factor': pd.Series([1.0,     0.01,   0.1,    0.1,    0.01,   0.0,     0.0,     0.01,   0.01,   0.01,    0.10,    0.00,      0.01,   0.0], index=layers).to_dict(),
            'n_imports': 0.0, # Number of new cases per day -- can be varied over time as part of the interventions
            'start_day': input_args.start_calibration_date,
            'end_day':   input_args.end_calibration_date,
            'analyzers': cv.age_histogram(datafile=agedatafile, edges=np.linspace(0, 75, 16), days=[8, 54]), # These days correspond to dates 9 March and 24 April, which is the date window in which qld has published age-disaggregated case counts
            'verbose': .1}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    
    beta_ints = define_beta_changes(betasfile, layers)             
    sim.pars['interventions'].extend(beta_ints)

    # # Testing of symptomatic cases
    # symp_prob_prelockdown = 0.08    # Limited testing pre lockdown
    # symp_prob_prelockdown_01 = 0.1 # 
    # symp_prob_prelockdown_02 = 0.2  #
    # symp_prob_prelockdown_03 = 0.3  #
    # symp_prob_prelockdown_04 = 0.4  #
    # symp_prob_prelockdown_05 = 0.35 #
    # symp_prob_lockdown = 0.3        # Increased testing during lockdown
    # symp_prob_postlockdown = 0.45   # Testing since lockdown
    # sim.pars['interventions'].append(cv.test_prob(start_day=start_day, 
    #                                               end_day='2020-02-29', 
    #                                               symp_prob=symp_prob_prelockdown, 
    #                                               asymp_quar_prob=0.001, do_plot=False))
    
    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-02-29', 
    #                                               end_day='2020-03-07', 
    #                                               symp_prob=symp_prob_prelockdown_01, 
    #                                               asymp_quar_prob=0.001, do_plot=False))

    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-07', 
    #                                               end_day='2020-03-10', 
    #                                               symp_prob=symp_prob_prelockdown_02, 
    #                                               asymp_quar_prob=0.001, do_plot=False))

    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-10', 
    #                                               end_day= '2020-03-15', 
    #                                               symp_prob=symp_prob_prelockdown_03, 
    #                                               asymp_quar_prob=0.001, do_plot=False))

    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-15', 
    #                                               end_day= '2020-03-24', 
    #                                               symp_prob=symp_prob_prelockdown_04, 
    #                                               asymp_quar_prob=0.001, do_plot=False))

    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-24', 
    #                                               end_day= '2020-04-07', 
    #                                               symp_prob=symp_prob_prelockdown_05, 
    #                                               asymp_quar_prob=0.001, do_plot=False))

    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-04-07', 
    #                                               end_day='2020-05-01', 
    #                                               symp_prob=symp_prob_lockdown, 
    #                                               asymp_quar_prob=0.001,do_plot=False))
    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-05-01', 
    #                                               symp_prob=symp_prob_postlockdown, 
    #                                               asymp_quar_prob=0.001,do_plot=True))

    
    # sim.pars['interventions'].append(cv.test_prob(start_day='2020-05-01', 
    #                                               symp_prob=symp_prob_postlockdown, 
    #                                               asymp_quar_prob=0.001,do_plot=True))


    data = pd.read_csv(datafile, parse_dates=['date'])
    if input_args.new_tests_mode == 'raw':
       this_column = 'new_tests_raw'
    else:
       this_column = 'new_tests'
    new_tests = data[this_column].to_list()

    #import pdb; pdb.set_trace()
    sim.pars['interventions'].append(cv.test_num(daily_tests=new_tests))


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

# Start setting up to run
# NB, this file assumes that you've already generated a population file saved in the same folder as this script, called qldpop.pop

if __name__ == '__main__':
    
    T = sc.tic()
    
    # Inputs
    inputsfolder = 'inputs'
    datafile = f'{inputsfolder}/qld_epi_data_calibration_qld-health.csv'
    agedatafile = f'{inputsfolder}/qld_demo_data_abs.csv'
    populationfile = f'{inputsfolder}/qldppl.pop'
    betasfile = f'{inputsfolder}/qld_model_layer_betas.csv'

    # Load argparse
    args = parser.parse_args()
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
    msim = cv.MultiSim(base_sim=sim)
    msim.run(n_runs=args.nruns, reseed=True, noise=0)
    msim_filename = f"{simfolder}/qld_{args.label}_{args.new_tests_mode}_numtests_{args.start_calibration_date}_{args.end_calibration_date}_{args.global_beta:.{4}f}_{args.init_seed_infections:02d}.obj"
    msim.save(msim_filename)
   
    # Plot all sims together 
    msim.reduce()
    msim_fig = msim.plot(do_show=False)
    msim_fig_filename = f"{figfolder}/qld_{args.label}_{args.new_tests_mode}_numtests_{args.start_calibration_date}_{args.end_calibration_date}_{args.global_beta:.{4}f}_{args.init_seed_infections:02d}_msim_fig.png"
    msim_fig.savefig(msim_fig_filename, dpi=100)
    plt.close('all')

    # Calculate fits 
    fit_pars_dict = {'absolute':True,
                     'use_median':True,
                     'font-size': 14}

    # Calculate fits independentely
    fitting_list = []
    for this_sim in msim.sims: 
        fitting_list.append(this_sim.compute_fit(keys=['new_diagnoses', 'cum_diagnoses', 'cum_deaths'],
                            weights= [4.0, 2.0, 1.0],
                            **fit_pars_dict))
        # Save list of fits
    fits_filename = f"{simfolder}/qld_{args.label}_{args.new_tests_mode}_numtests_{args.start_calibration_date}_{args.end_calibration_date}_{args.global_beta:.{4}f}_{args.init_seed_infections:02d}_fit.obj"
    sc.saveobj(filename=fits_filename, obj=fitting_list)
    fit_fig_filename = f"{figfolder}/qld_{args.label}_{args.new_tests_mode}_numtests_{args.start_calibration_date}_{args.end_calibration_date}_{args.global_beta:.{4}f}_{args.init_seed_infections:02d}_fit_fig.png"
    
    fit_fig = fitting_list[0].plot(do_show=False)
    fit_fig[0].savefig(fit_fig_filename, dpi=100)
    plt.close('all')
        