#!/usr/bin/env python
# coding: utf-8

"""
Create an instance of People() for Queensland
"""

import covasim as cv
import pandas as pd
import sciris as sc
import contacts as co
import data
import parameters
import utils
import functools
import numpy as np

def make_people(seed=None, pop_size=200000, pop_infected=50, 
                savepeople=True, popfile='qldppl.pop', 
                savepopdict=False, popdictfile='qdlpopdict.pop'):
    """
    Generate  popdict() and People() for Queensland population
    """

    db_name  = 'input_data_Australia_bkup'
    epi_name = 'epi_data_Australia' # Not sure why epi datafile needs to be passed in here, but difficult to remove this dependency

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'social']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    sim_pars = {'pop_size': pop_size,
                'pop_infected': pop_infected,
                'pop_scale': 10,
                'rescale': 1} # Pass in a minimal set of sim pars

    # return data relevant to each specified location in "locations"
    loc_data = data.read_data(locations=['QLD'],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end={'QLD':'2020-07-13'})

    # setup parameters object for this simulation
    params = parameters.setup_params(location='QLD',
                                     loc_data=loc_data,
                                     sim_pars=sim_pars)


    utils.set_rand_seed({'seed': seed})
    params.pars['rand_seed'] = seed

    people, popdict = co.make_people(params)
    if savepeople: sc.saveobj(popfile, people)
    if savepopdict: sc.saveobj(popdictfile, popdict)
    return people, popdict


if __name__ == '__main__':
  
  T = sc.tic()
  people, popdict = make_people(seed=42)
  sc.toc(T)
  