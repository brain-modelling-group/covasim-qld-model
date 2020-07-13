from pathlib import Path

import covasim as cv
import pandas as pd

import contacts as co
import data
import parameters
import policy_updates
import sciris as sc
import utils


def get_sim(location: str, db_name: str, epi_name: str, all_lkeys: list, dynamic_lkeys: list, user_pars: dict, metapars: dict):
    """
    Produce a cv.Sim for a given location

    This loads the calibration and parameters from the db file and creates a `cv.Sim` instance. No policy interventions are
    loaded or otherwise created. However, the dynamic contact layer intervention is created by this routine as it is
    an intrinsic attribute of the dynamic contact layers specified in `dynamic_lkeys`.

    Args:
        location: Name of a supported location e.g. 'Victoria'
        db_name: Name of databook. Must be contained in 'data' folder relative to `utils.py` i.e. `./utils.py` implies `./data/{db_name}.xlsx`. Example would be `db_name='input_data_Australia'`
        epi_name: Name of epi data.  Must be contained in 'data' folder relative to `utils.py` i.e. `./utils.py` implies `./data/{epi_name}.csv`. Example would be `epi_name='epi_data_Australia'`
        all_lkeys: List of all contact layers. Dynamic contact layers in `dynamic_lkeys` should also appear in this list
        dynamic_lkeys: List of contact layer names that need to be dynamically updated via an Intervention (also created by this function)
        user_pars: Some parameters that end up somewhere in cv.Sim.pars
        metapars: Some parameters that end up somewhere in cv.Sim.pars

    Returns: A cv.Sim object

    """

    assert set(dynamic_lkeys).issubset(all_lkeys), 'Some dynamic layers names do not appear in the list of all contact layers'

    # return data relevant to each specified location in "locations"
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

    #people, popdict = co.make_people(params)

    # setup simulation for this location
    sim = cv.Sim(pars=params.pars,
                 datafile=None,
                 pop_size=params.pars['pop_size'])

    # The UpdateNetworks 'intervention' is actually the implementation of random networks without any perturbations to connectivity
    # Therefore, we should create this intervention at this point at the same time as the layers are defined since it doesn't depend
    # on or specify any scenarios
    sim.pars['interventions'].append(policy_updates.UpdateNetworks(layers=dynamic_lkeys, contact_numbers=params.pars['contacts'], popdict=popdict))

    sim.initialize()

    return sim, params


def get_victoria_sim(n_runs: int = 2, n_days: int = 20, pop_infected: int = 1, pop_size: int = 1e4):
    """
    Produce a cv.Sim for Victoria with no policies

    This function loads Victoria parameters and returns a `cv.Sim` suitable for running outbreak scenarios

    Args:
        n_runs: Number of simulations to perform (with different seeds)
        n_days: Number of days of simulate
        pop_infected: Number of seed infections (default=1)
        pop_size: Number of people in simulation (default=1e4) - should be much larger than the number of infections in the outbreak
                  (so for example it would need to be bigger if `n_days` is large)

    Returns:
        A cv.Sim for Victoria

    """

    # INPUT SPECIFICATION
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
                'verbose': 1,
                'rand_seed': 1}

    utils.set_rand_seed(metapars)  # Set the seed in the main process before constructing the sim and scenario
    sim, params = get_sim(location, db_name, epi_name, all_lkeys, dynamic_lkeys, user_pars, metapars)
    return sim, params


def run_victoria_scen(scen_name: str, scen_policies: list, sim: cv.Sim, params: parameters.Parameters, ncpus: int = 2) -> cv.Scenarios:
    """
    Run Victoria outbreak scenario

    This function
    - Creates a Sim for Victoria with zero infections and no active policies
    - Turns on the policies specified in the input to this function
    - Seeds 1 infection on day 1
    - Runs up to `n_days` with as many runs as specified in this function input
    - Returns the `cv.Scenarios` object containing the results

    Args:
        scen_name: The name to assign to this scenario
        scen_policies: A list of active policies e.g. ['lockdown', 'beach0', 'beach2',...]
        sim: A `cv.Sim` (would usually be produced by `get_sim()`
        params: `covasim-australia` `Parameters` instance (would usually be produced by `get_sim()`
        ncpus: How many CPUs to use during parallel execution

    Returns: A `cv.Scenarios` instance with completed simulation results

    """

    # INITIALIZE INTERVENTIONS
    interventions = []

    # SET BETA POLICIES
    beta_schedule = policy_updates.PolicySchedule(params.pars["beta_layer"], params.policies['beta_policies'])  # create policy schedule with beta layer adjustments
    for policy in scen_policies:
        if policy in beta_schedule.policies:
            print(f'Adding beta policy {policy}')
            beta_schedule.start(policy, 0)
    interventions.append(beta_schedule)

    # SET TESTING
    interventions.append(cv.test_num(daily_tests=params.extrapars["future_daily_tests"],
                                     symp_test=params.extrapars['symp_test'],
                                     quar_test=params.extrapars['quar_test'],
                                     sensitivity=params.extrapars['sensitivity'],
                                     test_delay=params.extrapars['test_delay'],
                                     loss_prob=params.extrapars['loss_prob']))

    # SET TRACING
    interventions.append(cv.contact_tracing(trace_probs=params.extrapars['trace_probs'],
                                            trace_time=params.extrapars['trace_time'],
                                            start_day=0))
    tracing_app, id_checks = policy_updates.make_tracing(trace_policies=params.policies["tracing_policies"])
    if tracing_app is not None:
        interventions.append(tracing_app)
    if id_checks is not None:
        interventions.append(id_checks)

    # SET CLIPPING POLICIES
    for policy, clip_attributes in params.policies['clip_policies'].items():
        if policy in scen_policies:
            print(f'Adding clipping policy {policy}')
            interventions.append(cv.clip_edges(days=0,
                                               layers=clip_attributes['layers'],
                                               changes=clip_attributes['change']))

    # CREATE AND RUN cv.Scenarios OBJECT
    scenarios = {}
    scenarios[scen_name] = {'name': scen_name,
                            'pars': {'interventions': interventions}
                            }
    cova_scen = cv.Scenarios(sim=sim,
                             metapars=params.metapars,
                             scenarios=scenarios)
    cova_scen.run(keep_people=True, verbose=0, par_args={'ncpus': ncpus})

    return cova_scen


if __name__ == '__main__':

    n_cpus = 2
    n_runs = 10
    n_days = 21

    rootdir = Path(__file__).parent

    # Read the packages file
    packages = pd.read_excel(rootdir/'policy_packages.xlsx',index_col=0)
    packages = packages.T
    packages = packages.to_dict(orient='index')
    packages = {name:[policy for policy, active in package.items() if not pd.isnull(active)] for name, package in packages.items()}

    with sc.Timer(label='Create sim') as t:
        sim, params = get_victoria_sim(n_runs=n_runs, n_days=n_days)

    for name, policies in packages.items():
        with sc.Timer(label=f'Scenario "{name}"') as t:
            cova_scen = run_victoria_scen(name, policies, sim, params, n_cpus)
            cova_scen.save(rootdir/f'{name}.scen')
