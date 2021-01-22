#!/usr/bin/env python
# coding: utf-8

"""
Create an instance of People() for Queensland
"""

import covasim as cv
import pandas as pd
import sciris as sc

import covasim_australia.contacts as co
import covasim_australia.data as data
import covasim_australia.parameters as parameters
import covasim_australia.utils as utils
import functools
import numpy as np

def make_qld_people(seed=None, pop_size=200000, pop_infected=50, 
                savepeople=True, popfile='qldppl.pop', 
                savepopdict=False, popdictfile='qdlpopdict.pop'):
    """
    Generate  popdict() and People() for Queensland population
    """
    location = 'QLD'
    db_name  = 'input_data_Australia'
    epi_name = 'qld_health_epi_data.csv' # Not sure why epi datafile needs to be passed in here, but difficult to remove this dependency

    all_lkeys = ['H', 'S', 'W', 'C', 
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

    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    user_pars = {'pop_size': pop_size,
                #'pop_infected': pop_infected,
                'pop_scale': 25.5,
                'rescale': 1,
                'calibration_end': None
                } # Pass in a minimal set of sim pars

    #user_pars, _ = utils.clean_pars(user_pars, [location])

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=[location],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end={'QLD':'2020-09-30'})


    loc_data = all_data

    # setup parameters object for this simulation
    params = parameters.setup_params(location=location,
                                     loc_data=loc_data,
                                     sim_pars=user_pars)



    utils.set_rand_seed({'seed': seed})
    params.pars['rand_seed'] = seed

    people, popdict = co.make_people(params)
    if savepeople: 
        sc.saveobj(popfile, people)
    if savepopdict: 
        sc.saveobj(popdictfile, popdict)
    return people, popdict


if __name__ == '__main__':
  
  T = sc.tic()
  people, popdict = make_qld_people(seed=42)
  sc.toc(T)
  