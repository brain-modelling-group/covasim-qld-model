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


def load_policies():
    """
    Load policy packages from Excel file
    """
    packages = pd.read_excel('policy_packages.xlsx', index_col=0)
    packages = packages.T
    packages = packages.to_dict(orient='index')
    packages = {name: [policy for policy, active in package.items() if not pd.isnull(active)] for name, package in packages.items()}
    return packages


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


def make_sim(seed=None, params=None, load_pop=True, popfile='nswppl.pop', popdict='nswpopdict.pop', policies=None):
    # setup simulation for this location
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=popfile,
                 rand_seed=seed,
                 pop_size=params.pars['pop_size'],
                 load_pop=load_pop)

    # Add interventions
    sim.pars['interventions'].append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys, contact_numbers=params.pars['contacts'], popdict=popdict))

    # Beta policies
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])  # create policy schedule with beta layer adjustments
    for policy in policies:
        if policy in beta_schedule.policies:
            if sim['verbose']:
                print(f'Adding beta policy {policy}')
            beta_schedule.start(policy, 0)
    sim.pars['interventions'].append(beta_schedule)

    # Testing
    sim.pars['interventions'].append(cv.test_num(daily_tests=params.extrapars["future_daily_tests"],
                                                 symp_test=params.extrapars['symp_test'],
                                                 quar_test=params.extrapars['quar_test'],
                                                 sensitivity=params.extrapars['sensitivity'],
                                                 test_delay=params.extrapars['test_delay'],
                                                 loss_prob=params.extrapars['loss_prob']))

    # Tracing
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                                        trace_time=params.extrapars['trace_time'],
                                                        start_day=0))
    tracing_app, id_checks = policy_updates.make_tracing(trace_policies=params.policies["tracing_policies"])
    if tracing_app is not None:
        sim.pars['interventions'].append(tracing_app)
    if id_checks is not None:
        sim.pars['interventions'].append(id_checks)

    # Clipping
    for policy, clip_attributes in params.policies['clip_policies'].items():
        if policy in policies:
            if sim['verbose']:
                print(f'Adding clipping policy {policy}')
            sim.pars['interventions'].append(cv.clip_edges(days=0,
                                                           layers=clip_attributes['layers'],
                                                           changes=clip_attributes['change']))



    return sim


def run_sim(seed=None, params=None, load_pop=True, popfile='nswppl.pop', popdict='nswpopdict.pop', policies=None):
    """
    Run a single outbreak simulation
    """

    sim = make_sim(seed=seed, params=params, load_pop=load_pop, popfile=popfile, popdict=popdict, policies=policies)
    sim.run()
    return sim


T = sc.tic()
params = make_pars(location='NSW', pop_size=100e3, pop_infected=150)
policies = load_policies()
popdict = sc.loadobj('nswpopdict.pop')
# people, popdict = make_people(seed=1, params=params, savepeople=True, popfile='nswppl.pop', savepopdict=True, popdictfile='nswpopdict.pop')
sim = run_sim(seed=1, params=params, load_pop=True, popfile='nswppl.pop', popdict=popdict, policies=policies)

# Plotting
to_plot = sc.objdict({
    'Diagnoses': ['cum_diagnoses'],
    'Daily diagnoses': ['new_diagnoses'],
    'Deaths': ['cum_deaths'],
    'Daily deaths': ['new_deaths'],
    'Total infections': ['cum_infections'],
    'Cumulative tests': ['cum_tests'],
    'New infections per day': ['new_infections'],
    'New tests': ['new_tests'],
    })


sim.plot(to_plot=to_plot, do_save=True, do_show=False, fig_path=f'nsw_calibration.png',
         legend_args={'loc': 'upper left'}, axis_args={'hspace':0.4}, interval=21)

#if do_save:
#    sim.save(f'nigeria_{which}_{length}.sim')


sc.toc(T)