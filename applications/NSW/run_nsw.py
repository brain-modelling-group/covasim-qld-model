import covasim as cv
import pandas as pd
import contacts as co
import data
import parameters
import policy_updates
import sciris as sc
import utils
import functools
import numpy as np
import sys


def make_pars(location='NSW', pop_size=100e3, pop_infected=150):
    """
    Load Australian parameters from Excel files
    """

    db_name = 'input_data_Australia'
    epi_name = 'epi_data_Australia'

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'child_care', 'social']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    sim_pars = {'pop_size': int(pop_size),
                'pop_infected': pop_infected,
                'pop_scale': 1,
                'rescale': 0,
                'beta': 0.065,
                'start_day': '2020-03-01',
                'end_day': '2020-07-13',
                'verbose': 0.1}

    metapars = {'noise': 0.0,
                'verbose': 0}

    # return data relevant to each specified location in "locations"
    loc_data = data.read_data(locations=[location],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end={'NSW':'2020-07-13'})

    # setup parameters object for this simulation
    params = parameters.setup_params(location=location,
                                     loc_data=loc_data,
                                     metapars=metapars,
                                     sim_pars=sim_pars)

    return params


def make_people(seed=None, params=None, savepeople=True, popfile='nswppl.pop', savepopdict=False, popdictfile='nswpopdict.pop'):
    """
    Produce popdict and People
    """

    utils.set_rand_seed({'seed': seed})
    params.pars['rand_seed'] = seed

    people, popdict = co.make_people(params)
    if savepeople: sc.saveobj(popfile, people)
    if savepopdict: sc.saveobj(popdictfile, popdict)
    return people, popdict


def make_sim(seed=None, params=None, load_pop=True, popfile='nswppl.pop'):
    # setup simulation for this location
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=popfile,
                 rand_seed=seed,
                 pop_size=params.pars['pop_size'],
                 load_pop=load_pop)

    # Add interventions


    return sim


def run_sim(seed=None, params=None, load_pop=True, popfile='nswppl.pop'):
    """
    Run a single outbreak simulation
    """

    sim = make_sim(seed, params, load_pop=load_pop, popfile=popfile)
    sim.run()
    return sim


T = sc.tic()
params = make_pars(location='NSW', pop_size=100e3, pop_infected=150)
# people, popdict = make_people(seed=1, params=params, savepeople=True, popfile='nswppl.pop', savepopdict=True, popdictfile='nswpopdict.pop')
sim = run_sim(seed=1, params=params, load_pop=True, popfile='nswppl.pop')
sc.toc(T)