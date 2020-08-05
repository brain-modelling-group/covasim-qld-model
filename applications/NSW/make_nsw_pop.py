import covasim as cv
import pandas as pd
import sciris as sc
import contacts as co
import data
import parameters
import utils
import functools
import numpy as np
#import sys


def make_people(seed=None, pop_size=100e3, pop_infected=150, savepeople=True, popfile='nswppl.pop', savepopdict=False, popdictfile='nswpopdict.pop'):
    """
    Produce popdict and People
    """

    db_name = 'input_data_Australia'
    epi_name = 'epi_data_Australia' # Not sure why epi datafile needs to be passed in here, but difficult to remove this dependency

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'social']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    sim_pars = {'pop_size': int(pop_size),
                'pop_infected': pop_infected,
                'pop_scale': 1,
                'rescale': 1} # Pass in a minimal set of sim pars

    # return data relevant to each specified location in "locations"
    loc_data = data.read_data(locations=['NSW'],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end={'NSW':'2020-07-13'})

    # setup parameters object for this simulation
    params = parameters.setup_params(location='NSW',
                                     loc_data=loc_data,
                                     sim_pars=sim_pars)


    utils.set_rand_seed({'seed': seed})
    params.pars['rand_seed'] = seed

    people, popdict = co.make_people(params)
    if savepeople: sc.saveobj(popfile, people)
    if savepopdict: sc.saveobj(popdictfile, popdict)
    return people, popdict



T = sc.tic()
people, popdict = make_people(seed=1, pop_size=100e3, pop_infected=150, savepeople=True, popfile='nswppl.pop', savepopdict=True, popdictfile='nswpopdict.pop')
sc.toc(T)