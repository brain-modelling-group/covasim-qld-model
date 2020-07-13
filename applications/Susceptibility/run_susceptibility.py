from pathlib import Path

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

from covasim import misc
misc.git_info = lambda: None  # Disable this function to increase performance slightly


def run_australia_outbreak(seed, params, scen_policies):

    utils.set_rand_seed({'seed':seed})  # Set the seed before constructing the people

    people, popdict = co.make_people(params)

    # setup simulation for this location
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=people,
                 pop_size=params.pars['pop_size'],
                 load_pop=True,
                 save_pop=False)

    # ADD DYNAMIC LAYERS INTERVENTION
    sim.pars['interventions'].append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys, contact_numbers=params.pars['contacts'], popdict=popdict))

    # SET BETA POLICIES
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])  # create policy schedule with beta layer adjustments
    for policy in scen_policies:
        if policy in beta_schedule.policies:
            print(f'Adding beta policy {policy}')
            beta_schedule.start(policy, 0)
    sim.pars['interventions'].append(beta_schedule)

    # SET TESTING
    sim.pars['interventions'].append(cv.test_num(daily_tests=params.extrapars["future_daily_tests"],
                                     symp_test=params.extrapars['symp_test'],
                                     quar_test=params.extrapars['quar_test'],
                                     sensitivity=params.extrapars['sensitivity'],
                                     test_delay=params.extrapars['test_delay'],
                                     loss_prob=params.extrapars['loss_prob']))

    # SET TRACING
    sim.pars['interventions'].append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                            trace_time=params.extrapars['trace_time'],
                                            start_day=0))
    tracing_app, id_checks = policy_updates.make_tracing(trace_policies=params.policies["tracing_policies"])
    if tracing_app is not None:
        sim.pars['interventions'].append(tracing_app)
    if id_checks is not None:
        sim.pars['interventions'].append(id_checks)

    # SET CLIPPING POLICIES
    for policy, clip_attributes in params.policies['clip_policies'].items():
        if policy in scen_policies:
            print(f'Adding clipping policy {policy}')
            sim.pars['interventions'].append(cv.clip_edges(days=0,
                                               layers=clip_attributes['layers'],
                                               changes=clip_attributes['change']))

    sim.run()
    return sim



if __name__ == '__main__':

    n_cpus = 2
    n_runs = 10
    n_days = 31
    pop_size = 1e4
    pop_infected = 1 # Number of initial infections
    rootdir = Path(__file__).parent

    # Read the packages file
    packages = pd.read_excel(rootdir/'policy_packages.xlsx',index_col=0)
    packages = packages.T
    packages = packages.to_dict(orient='index')
    packages = {name:[policy for policy, active in package.items() if not pd.isnull(active)] for name, package in packages.items()}

    # LOAD PARAMETERS
    location = 'Victoria'  # the list of locations for this analysis
    db_name = 'input_data_Australia'  # the name of the databook
    epi_name = 'epi_data_Australia'

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'pSport', 'cSport', 'beach', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'national_parks', 'public_parks', 'large_events', 'child_care', 'social', 'aged_care']
    dynamic_lkeys = ['C', 'beach', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'national_parks', 'public_parks', 'large_events']  # layers which update dynamically (subset of all_lkeys)

    user_pars = {location: {'pop_size': int(pop_size),
                            'pop_infected': pop_infected,
                            'pop_scale': 1,
                            'rescale': 0,
                            'beta': 0.065,  # TODO - check where this value came from
                            'n_days': n_days,
                            'calibration_end': None}}

    metapars = {'n_runs': n_runs,
                'noise': 0.0,
                'verbose': 1}
                # 'rand_seed': seed}

    user_pars, calibration_end = utils.clean_pars(user_pars, [location])

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=[location],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end=calibration_end)

    loc_data = all_data[location]
    loc_pars = user_pars[location]

    # setup parameters object for this simulation
    params = parameters.setup_params(location=location,
                                     loc_data=loc_data,
                                     metapars=metapars,
                                     user_pars=loc_pars)


    for name, policies in packages.items():
        with sc.Timer(label=f'Scenario "{name}"') as t:

            sim_fcn = functools.partial(run_australia_outbreak, params=params, scen_policies=policies)
            sims = sc.parallelize(sim_fcn, np.arange(n_runs))

            sc.saveobj(rootdir/f'{name}.sims', sims)
            # cova_scen.save()
