import covasim as cv
import covasim.utils as cvu
import pandas as pd

import contacts as co
import data
import parameters
import policy_updates
import utils
import numpy as np

def load_packages(fname) -> dict:
    """
    Load policy packages from CSV file

    CSV file should just be a table with rows for packages, columns
    for policies, and non-empty cells if the package contains a policy

    Args:
        fname: File name to load

    Returns: Dictionary `{package_name:[policies]}`

    """

    packages = pd.read_csv(fname, index_col=0)
    full_names = packages['full_name'].to_dict()
    del packages['full_name']
    packages = packages.to_dict(orient='index')
    packages = {name: [policy for policy, active in package.items() if not pd.isnull(active)] for name, package in packages.items()}
    return packages, full_names

def load_scenarios(fname) -> dict:
    """
    Load scenarios from CSV file

    CSV file
    Args:
        fname: File name to load

    Returns: Dictionary {scenario_name:{parameter:value}}

    """

    scenarios = pd.read_csv(fname, index_col=0)
    full_names = scenarios['full_name'].to_dict()
    del scenarios['full_name']
    scenarios.fillna(value=scenarios.iloc[0,:], inplace=True)
    scenarios = scenarios.to_dict(orient='index')
    return scenarios, full_names

def load_australian_parameters(location: str = 'Victoria', pop_size: int = 1e4, n_infected: int = 1, n_days: int = 31) -> parameters.Parameters:
    """
    Load Australian parameters

    Args:
        location: Location string for an Australian location e.g. 'Victoria'
        pop_size: Number of agents
        n_infected: Number of initial infections
        n_days:

    Returns:

    """

    db_name = 'input_data_Australia'  # the name of the databook
    epi_name = 'epi_data_Australia'

    all_lkeys = ['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar',
                 'transport', 'public_parks', 'large_events', 'child_care', 'social','aged_care']
    dynamic_lkeys = ['C', 'entertainment', 'cafe_restaurant', 'pub_bar',
                     'transport', 'public_parks', 'large_events']

    user_pars = {location: {'pop_size': int(pop_size),
                            'pop_infected': 0,
                            'pop_scale': 1,
                            'rescale': 0,
                            'beta': 0.0525,
                            'n_days': n_days,
                            'calibration_end': None,
                            'verbose': 0}}

    metapars = {'noise': 0.0,
                'verbose': 0}

    user_pars, calibration_end = utils.clean_pars(user_pars, [location])

    # return data relevant to each specified location in "locations"
    all_data = data.read_data(locations=[location],
                              db_name=db_name,
                              epi_name=epi_name,
                              all_lkeys=all_lkeys,
                              dynamic_lkeys=dynamic_lkeys,
                              calibration_end=calibration_end)

    loc_data = all_data
    loc_pars = user_pars[location]

    # setup parameters object for this simulation
    params = parameters.setup_params(location=location,
                                     loc_data=loc_data,
                                     metapars=metapars,
                                     sim_pars=loc_pars)

    params.test_prob = {
        'symp_prob': 0.1,  # Overall probability of being tested if symptomatic
        'asymp_prob': 0.00,  # Probability
        'symp_quar_prob': 1.0,  # Someone who is quarantining and has symptoms has this probability of testing on any given day
        'asymp_quar_prob': 0.0,
        'test_delay': 1, # Number of days for test results to be processed
        'swab_delay': 2, # Number of days people wait after symptoms before being tested
        'test_isolation_compliance': 0,
        'leaving_quar_prob': 0,
    }

    params.seed_infections = {1: n_infected}
    params.extrapars['trace_capacity'] = 250

    return params


def get_australia_outbreak(seed: int, params: parameters.Parameters, scen_policies: list, people=None, layer_members=None) -> cv.Sim:
    """
    Produce outbreak simulation but don't run it

    Args:
        seed: Integer seed
        params: `Parameters` object (e.g. returned by `load_australian_parameters()`
        scen_policies: List of policies to use e.g. `['outdoor2','schools'] (should appear on the 'policies' sheet in the input data Excel file)
        people: Optionally call `co.make_people()` externally and pass in the people and layer_members

    Returns: A `cv.Sim` instance, before execution

    """

    cvu.set_seed(seed)  # Set the seed before constructing the people
    params.pars['rand_seed'] = seed  # Covasim resets the seed again internally during initialization...

    if people is None:
        people, layer_members = co.make_people(params)
    else:
        assert layer_members is not None, 'If specifying people, popdict must be provided as well'

    # setup simulation for this location
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 popfile=people,
                 pop_size=params.pars['pop_size'],
                 load_pop=True,
                 save_pop=False)

    # ADD DYNAMIC LAYERS INTERVENTION
    sim.pars['interventions'].append(policy_updates.UpdateNetworks(layers=params.dynamic_lkeys, contact_numbers=params.pars['contacts'], include_inds=layer_members, dispersion=params.layerchars['dispersion']))

    # SET TRACING
    sim.pars['interventions'].append(utils.SeedInfection(params.seed_infections))

    # SET BETA POLICIES
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])  # create policy schedule with beta layer adjustments
    for policy in scen_policies:
        if policy in beta_schedule.policies:
            if sim['verbose']:
                print(f'Adding beta policy {policy}')
            beta_schedule.start(policy, 0)
    sim.pars['interventions'].append(beta_schedule)

    # SET TESTING
    sim.pars['interventions'].append(utils.test_prob_with_quarantine(
        symp_prob=params.test_prob['symp_prob'],
        asymp_prob=params.test_prob['asymp_prob'],
        symp_quar_prob=params.test_prob['symp_quar_prob'],
        asymp_quar_prob=params.test_prob['asymp_quar_prob'],
        test_delay=params.test_prob['test_delay'],
        swab_delay=params.test_prob['swab_delay'],
        test_isolation_compliance=params.test_prob['test_isolation_compliance'],
        leaving_quar_prob=params.test_prob['leaving_quar_prob'],
    ))

    # SET TRACING
    sim.pars['interventions'].append(utils.limited_contact_tracing(trace_probs={'H': params.extrapars['trace_probs']['H']},
                                                                   trace_time={'H': params.extrapars['trace_time']['H']},
                                                                   start_day=0,
                                                                   capacity=np.inf,
                                                                   ))

    # Add tracing intervention for other layers
    # Remove the household layer from trace_probs because they will be traced separately
    del params.extrapars['trace_probs']['H']
    del params.extrapars['trace_time']['H']
    sim.pars['interventions'].append(utils.limited_contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                                                   trace_time=params.extrapars['trace_time'],
                                                                   start_day=0,
                                                                   capacity=params.extrapars['trace_capacity'],
                                                                   dynamic_layers=params.dynamic_lkeys))

    sim.pars['interventions'].append(policy_updates.AppBasedTracing(name='tracing_app',
                                                                    layers=['H', 'S', 'W', 'C', 'church', 'cSport', 'entertainment', 'cafe_restaurant', 'pub_bar', 'transport', 'public_parks', 'large_events', 'child_care', 'social', 'aged_care'],
                                                                    coverage=[0.2],
                                                                    days=[0]))

    # SET CLIPPING POLICIES
    for policy, clip_attributes in params.policies['clip_policies'].items():
        if policy in scen_policies:
            if sim['verbose']:
                print(f'Adding clipping policy {policy}')
            sim.pars['interventions'].append(cv.clip_edges(days=0,
                                                           layers=clip_attributes['layers'],
                                                           changes=clip_attributes['change']))

    if 'dynamic_masks' in scen_policies:
        print('Converting masks to dynamic policy')
        beta_schedule.remove('masks') # Remove masks from day 0
        dynamic_trigger = utils.DynamicTrigger(condition=mask_condition, action=mask_action, once_only=True)
        sim.pars['interventions'].insert(0, dynamic_trigger) # Make sure it runs before beta schedule

    return sim


def mask_condition(sim):
    return np.any(sim.people.diagnosed)

def mask_action(sim):
    for intervention in sim.pars['interventions']:
        if isinstance(intervention, policy_updates.PolicySchedule):
            print('Triggered masks on day %d' % (sim.t))
            intervention.start('masks', sim.t)
