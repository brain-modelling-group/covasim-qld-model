#!/usr/bin/env python
# coding: utf-8
"""
(RE)calibration of QLD model.

We initialized the model on February 15th, and run simulations until June 30th 2020.
by seeding X infections in the model population.

The number of seed infections chosen as part of the calibration process. 
The model was fitted to data  on  
(1)  the  number  of  tests  conducted  and  
(2)  the  daily  number  of  cases  diagnosed  in  QLD

How: by  performing  an  automated  search for the  values of the number of seed infections 
that *minimized the absolute differences between the model projections and the data*. 

We repeated the initialization 100 times (for each combination?), each time with 
a different set of 100 people infected at the beginning of the simulation.

Many simulation parameters are taken from calibrated NSW case:
https://github.com/optimamodel/covid_nsw/blob/master/run_nsw_tracing.py

# author: For QLD Paula Sanz-Leon, QIMRB, Aug-Dec 2020
"""

# Import scientific python
import pandas as pd
import numpy as np

# Import IDM/Optima code
import covasim as cv
import sciris as sc
import covasim_australia.utils as utils

# Add argument parser
import argparse


# Check covasim version is the one we actually need
cv.check_version('1.6.1', die=True)

parser = argparse.ArgumentParser()
parser.add_argument('--nruns', default=2, 
                               type=int, 
                               help='''Number of simulations to run per scenario. 
                                       Uses different PRNG seeds for each simulations.''')
parser.add_argument('--case', default='recalibration', 
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

parser.add_argument('--cluster_size', default=0, 
                              type=int, 
                              help='''The number of infected people entering QLD community on a given date (default, 2020-10-01)''')

parser.add_argument('--init_seed_infections', default=1, 
                               type=int, 
                               help='''Number of ppl infected at the beginning of the simulation.''')

parser.add_argument('--open_borders_date', default='2020-10-01', 
                              type=str, 
                              help='''The date at which borders are open (eg, '2020-09-21').''')

parser.add_argument('--start_calibration_date', default='2020-02-15', 
                              type=str, 
                              help='''The date at which calibration starts (default, '2020-02-15').''')

parser.add_argument('--end_calibration_date', default='2020-06-30', 
                              type=str, 
                              help='''The date at which calibration finishes (default, '2020-06-30').''')


args = parser.parse_args()


def make_sim(case_to_run, load_pop=True, popfile='qldppl.pop', datafile=None, agedatafile=None, input_args=None):
    start_day = args.start_calibration_date
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
            'pop_infected': args.init_seed_infections,   # Original population infedcted
            'pop_scale': 29,      # Population scales to 5.8M ppl in QLD
            'rescale': True,      # Population dynamics rescaling
            'rand_seed': 42,      # Random seed to use
            'rel_death_prob': 0.6,#
            'beta': 0.025,        # Overall beta to use for calibration portion of the simulations
                                  #   H        S       W       C   church   psport  csport    ent     cafe    pub     trans    park        event    soc
            'contacts':    pd.Series([4.0,    21.0,    5.0,    1.0,   20.0,   40.0,    30.0,    25.0,   19.00,  30.00,   25.00,   10.00,     50.00,   6.0], index=layers).to_dict(),
            'beta_layer':  pd.Series([1.0,     0.3,    0.2,    0.1,    0.04,   0.2,     0.1,     0.01,   0.04,   0.06,    0.16,    0.03,      0.01,   0.3], index=layers).to_dict(),
            'iso_factor':  pd.Series([0.2,     0.0,    0.0,    0.1,    0.0,    0.0,     0.0,     0.0,    0.0,    0.0,     0.0,     0.0,       0.0,    0.0], index=layers).to_dict(),
            'quar_factor': pd.Series([1.0,     0.1,    0.1,    0.2,    0.01,   0.0,     0.0,     0.0,    0.00,   0.0,     0.10,    0.00,      0.00,   0.0], index=layers).to_dict(),
            'n_imports': 0.1, # Number of new cases per day -- can be varied over time as part of the interventions
            'start_day': args.start_calibration_date,
            'end_day': args.end_calibration_date,
            'analyzers': cv.age_histogram(datafile=agedatafile, edges=np.linspace(0, 75, 16), days=[8, 54]), # These days correspond to dates 9 March and 24 April, which is the date window in which qld has published age-disaggregated case counts
            'verbose': .1}

    sim = cv.Sim(pars=pars,
                 datafile=datafile,
                 popfile=popfile,
                 load_pop=load_pop)

    # Create beta policies
    response00 = '2020-03-15' # Physical distancing, handwashing -- ongoing
    response01 = '2020-03-19' # Outdoors restricted to < 200 ppl
    response02 = '2020-03-21' # Enahnced screening and distancing within age care facilities
    lockdown00 = '2020-03-23' # Lockdown starts, churches close, restaurants/pubs close
                              # cSports cancelled, entratianment, large-events, pSports
    lockdown01 = '2020-03-25' # noncovid health services close - C-layer
    lockdown02 = '2020-03-26' # retail close - C layer
    parks00   = '2020-04-03'  # National parks close - public parks
    borders00 = '2020-04-03'  # Borders shut to all state
    beach00   = '2020-04-07'  # Beaches closes
    
    # relaxation dates 
    outdoors00 = '2020-03-30'   # Outdoors ok < 2 ppl
    beach01    = '2020-04-20'   # Beaches ok <2 ppl
    parks01    = '2020-05-01'   # national parks open
    church00   = '2020-05-16'   # Church 4sqm rule, 
    outdoors01 = '2020-05-16'   # outdoor ok <10 ppl
    beach02    = '2020-05-16'   # Beaches ok <10 ppl
    # reopening dates
    reopen01  = '2020-06-01' # reopen cSports, cinemas, social, beach, psport, shopping 
    reopen02  = '2020-06-15' # noncovid health services open
    reopen03  = '2020-07-03' # large events open
    borders01 = '2020-07-10' # regional travel open,
    schools   = ['2020-03-30', '2020-05-25']
    # shut borders again
    borders02 ='2020-08-05'  # effective border closure NSW, VIC, ACT
    borders03 ='2020-09-25'  # borders open to ACT
    borders04 ='2020-09-23'  # borders open to some parts of NSW

    # If using clip_edges, the value in 'changes' expreses the percentage % of edges that is preserved after clipping
    beta_ints = [cv.change_beta(days=[response00, response01]+schools, 
                                changes=[0.80, 0.80, 0.80, 0.9], 
                                layers=['S'], do_plot=False),
                 
                 cv.change_beta(days=[response00, response01, lockdown00, lockdown01, lockdown02, reopen01], 
                               changes=[0.95, 0.8, 0.4, 0.3, 0.2, 0.5], 
                               layers=['W'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                               changes=[0.0, 0.5], 
                               layers=['pSport'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01],
                               changes=[0.0, 0.8], 
                               layers=['cSport'], do_plot=False),

                 # Reduce overall beta to account for distancing, handwashing, etc
                 cv.change_beta([response00, response01, reopen01], [0.9, 0.8, 0.9], do_plot=False), 
                 
                 cv.change_beta(days=[lockdown00, reopen01, reopen02], 
                                changes=[1.2, 1.1, 1.], 
                                layers=['H'], do_plot=True),
                 
                 cv.change_beta(days=[lockdown00, church00], 
                                changes=[0.0, 0.6], 
                                layers=['church'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01, reopen02, reopen03], 
                                changes=[0.1, 0.3, 0.4, 0.5], 
                                layers=['social'], do_plot=False),
                 # Dynamic layers ['C', 'entertainment', 'cafe_restaurant', 
                 # 'pub_bar', 'transport', 'public_parks', 'large_events']
                 
                 cv.change_beta(days=[start_day, response01, lockdown01, lockdown02, reopen01, reopen02, borders02], 
                                changes=[3.0, 0.7, 0.67, 0.6, 0.7, 0.8, 0.9], 
                                layers=['C'], do_plot=True),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.0, 0.8], 
                                layers=['entertainment'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.1, 0.7], 
                                layers=['cafe_restaurant'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen01], 
                                changes=[0.0, 0.5], 
                                layers=['pub_bar'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, borders00, borders01, borders02], 
                                changes=[0.5, 0.4, 0.5, 0.2], 
                                layers=['transport'], do_plot=False),
                 
                 cv.change_beta(days=[outdoors00, parks00, parks01], 
                                changes=[0.4, 0.1, 0.5], 
                                layers=['public_parks'], do_plot=False),
                 
                 cv.change_beta(days=[lockdown00, reopen03], 
                                changes=[0.0, 0.6], 
                                layers=['large_events'], do_plot=False),
                 ]
    sim.pars['interventions'].extend(beta_ints)

    # Testing -
    symp_prob_prelockdown = 0.04    # Limited testing pre lockdown
    symp_prob_prelockdown_01 = 0.1  # 
    symp_prob_prelockdown_02 = 0.2  #
    symp_prob_prelockdown_03 = 0.3  #
    symp_prob_prelockdown_04 = 0.4  #
    symp_prob_prelockdown_05 = 0.35 #
    symp_prob_lockdown = 0.3        # Increased testing during lockdown
    symp_prob_postlockdown = 0.2   # Testing since lockdown
    sim.pars['interventions'].append(cv.test_prob(start_day=start_day, 
                                                  end_day='2020-03-07', 
                                                  symp_prob=symp_prob_prelockdown, 
                                                  asymp_quar_prob=0.001, do_plot=False))
    
    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-07', 
                                                  end_day='2020-03-15', 
                                                  symp_prob=symp_prob_prelockdown_01, 
                                                  asymp_quar_prob=0.001, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-15', 
                                                  end_day='2020-03-20', 
                                                  symp_prob=symp_prob_prelockdown_02, 
                                                  asymp_quar_prob=0.001, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-20', 
                                                  end_day= '2020-03-24', 
                                                  symp_prob=symp_prob_prelockdown_03, 
                                                  asymp_quar_prob=0.001, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-24', 
                                                  end_day= '2020-03-28', 
                                                  symp_prob=symp_prob_prelockdown_04, 
                                                  asymp_quar_prob=0.001, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-03-28', 
                                                  end_day= '2020-04-05', 
                                                  symp_prob=symp_prob_prelockdown_04, 
                                                  asymp_quar_prob=0.001, do_plot=False))

    sim.pars['interventions'].append(cv.test_prob(start_day='2020-04-05', 
                                                  end_day=reopen01, 
                                                  symp_prob=symp_prob_lockdown, 
                                                  asymp_quar_prob=0.001,do_plot=False))
    sim.pars['interventions'].append(cv.test_prob(start_day=reopen01, 
                                                  symp_prob=symp_prob_postlockdown, 
                                                  asymp_quar_prob=0.001,do_plot=True))

    # Tracing
    trace_probs = {'H': 1, 'S': 0.95, 
                   'W': 0.9, 'C': 0.05, 
                   'church': 0.5, 
                   'pSport': 0.8, 
                   'cSport': 0.5,
                   'entertainment': 0.1, 
                   'cafe_restaurant': 0.8, 
                   'pub_bar': 0.8, 
                   'transport': 0.8, 
                   'public_parks': 0.01, 
                   'large_events': 0.01, 
                   'social': 0.9}
    trace_time = {'H': 0, 'S': 2, 
                  'W': 2, 'C': 7, 
                  'church': 5, 
                  'pSport': 3, 
                  'cSport': 3, 
                  'entertainment': 7,
                  'cafe_restaurant': 7, 
                  'pub_bar': 7, 
                  'transport': 7, 
                  'public_parks': 14,  
                  'large_events': 14,
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
    # Settings
    
    case_to_run    = args.case
    # Filepaths
    inputsfolder = 'inputs'
    resultsfolder = 'results_recalibration'
    datafile = f'{inputsfolder}/qld_epi_data_wave_01_basic_stats.csv'
    agedatafile = f'{inputsfolder}/qld_epi_data_wave_01_age_cumulative.csv'
    populationfile = f'{inputsfolder}/qldppl.pop'

    # Create instance of simulator
    sim  = make_sim(case_to_run,
                    load_pop=True, 
                    popfile=populationfile, 
                    datafile=datafile, 
                    agedatafile=agedatafile,
                    input_args = args)

    results_path = f"{resultsfolder}/qld_{case_to_run}_{args.end_calibration_date}_{args.init_seed_infections:02d}.obj"

    
    # Run and plot
    if args.nruns > 1:
        msim = cv.MultiSim(base_sim=sim)
        msim.run(n_runs=args.nruns, reseed=True, noise=0)
        msim.save(results_path)
    else:
        sim.run()
        sim.save(results_path)

    sc.toc(T)