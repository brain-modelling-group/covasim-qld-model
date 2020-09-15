from celery import Celery, Task
from covasim import misc
import resurgence
import sciris as sc
import numpy as np
import covasim as cv
import covasim.utils as cvu
from celery.signals import after_setup_task_logger
import logging
import covasim_australia as cva
import pandas as pd

misc.git_info = lambda: None  # Disable this function to increase performance slightly

import os
broker = os.getenv('COVID_REDIS_URL', 'redis://127.0.0.1:6379')

# Create celery app
celery = Celery('resurgence')
celery.conf.broker_url = broker
celery.conf.result_backend = broker
celery.conf.task_default_queue = 'resurgence'
celery.conf.accept_content = ['pickle', 'json']
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_acks_late = True # Allow other servers to pick up tasks in case they are faster

# Quieter tasks
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    logger.setLevel(logging.WARNING)


def stop_calibration(sim, cases):
    # Pass in the cases dataframe
    # The result of `cases = pd.read_csv(cva.datadir / 'victoria' / 'new_cases.csv')`

    if sim.t < 30:
        return False # Run for at least 30 days to allow time for the epidemic to start

    cases = cases.copy()
    cases.index = cases['Date'].map(sim.day)
    data_cases = cases.loc[(cases.index>0) & (cases.index < sim.t),'vic'].sum() # use `< sim.t` to exclude `sim.t` as noted below

    model_cases = (sim.rescale_vec[:sim.t]*sim.results['new_diagnoses'][:sim.t]).sum()

    if abs(model_cases-data_cases)/data_cases > 0.1:
        # If the model differs from data by more than 10%
        print(f'{sim.pars["rand_seed"]=} {sim.t=} {model_cases=}, {data_cases=}, calibration rejected')
        return True

    return False

class CachePeopleTask(Task):
    people = None
    layer_members = None
    people_seed = None

class CacheProjectionTask(Task):
    people = None
    layer_members = None
    people_seed = None
    projection_sims = {}


@celery.task(base=CachePeopleTask)
def resurgence_calibration(params, beta, seed, people_seed):

    from resurgence import rootdir
    resultsdir = rootdir.parent/'results'
    resultsdir.mkdir(exist_ok=True, parents=True)

    if resurgence_calibration.people is None or resurgence_calibration.people_seed != people_seed:
        # Create and cache cv.People if required
        # If people haven't been generated, or if the people seed has changed. If the number of people has changed
        # then a hard error should occur later. In general, it's better to restart Celery entirely where possible
        cvu.set_seed(people_seed)
        params.pars['rand_seed'] = people_seed
        resurgence_calibration.people, resurgence_calibration.layer_members = cva.make_people(params)
        resurgence_calibration.people_seed = people_seed
    people = resurgence_calibration.people
    layer_members = resurgence_calibration.layer_members

    with sc.Timer(label='Create calibration simulation') as t:
        sim = resurgence.get_victoria_sim(params, beta, seed, sc.dcp(people), sc.dcp(layer_members), release_day=None)

    with sc.Timer(label='Run calibration simulation') as t:
        sim.run()

    accepted_calibration = True

    if not sim.results_ready:
        accepted_calibration = False # Calibration was rejected if execution ended early
        sim.finalize()
        # Truncate the arrays
        for k, result in sim.results.items():
            if isinstance(result, cv.Result):
                result.values = result.values[0:sim.t+1]
            else:
                sim.results[k] = sim.results[k][0:sim.t+1]

    df = cva.result_df(sim)

    return df, beta, seed, accepted_calibration


@celery.task(base=CacheProjectionTask)
def resurgence_projection(params, beta, calibration_seed, projection_seed, people_seed, release_day):
    """

    Args:
        params:
        beta: Beta value used from calibration for this run
        calibration_seed: Calibration seed
        projection_seed:
        people_seed:
        release_day:

    Returns:

    """

    from resurgence import rootdir


    if resurgence_projection.people is None or resurgence_projection.people_seed != people_seed:
        # Create and cache cv.People if required
        # If people haven't been generated, or if the people seed has changed. If the number of people has changed
        # then a hard error should occur later. In general, it's better to restart Celery entirely where possible
        cvu.set_seed(people_seed)
        params.pars['rand_seed'] = people_seed
        resurgence_projection.people, resurgence_projection.layer_members = cva.make_people(params)
        resurgence_projection.people_seed = people_seed
    people = resurgence_projection.people
    layer_members = resurgence_projection.layer_members

    if (beta, calibration_seed, release_day) in resurgence_projection.projection_sims:
        with sc.Timer(label='Copy calibration simulation') as _:
            sim = sc.dcp(resurgence_projection.projection_sims[(beta, calibration_seed, release_day)])
    else:
        with sc.Timer(label='Create calibration simulation') as _:
            sim = resurgence.get_victoria_sim(params, beta, calibration_seed, sc.dcp(people), sc.dcp(layer_members), release_day=release_day)

        with sc.Timer(label='Run to release day') as _:
            sim.run(until=release_day) # Run it up to the release day
            resurgence_projection.projection_sims[(beta, calibration_seed, release_day)] = sc.dcp(sim)

    sim['rand_seed'] = projection_seed
    with sc.Timer(label='Run projection') as _:
        sim.run(reset_seed=True)


    if not sim.results_ready:
        accepted_calibration = False # Calibration was rejected if execution ended early
        sim.finalize()
        # Truncate the arrays
        for k, result in sim.results.items():
            if isinstance(result, cv.Result):
                result.values = result.values[0:sim.t+1]
            else:
                sim.results[k] = sim.results[k][0:sim.t+1]

    df = cva.result_df(sim)

    # Note that saving the sim like this will serve as a full backup of the run but it will need to be copied over from
    # all remote machines
    resultsdir = rootdir.parent/'projection_results'
    resultsdir.mkdir(exist_ok=True, parents=True)
    sc.saveobj(resultsdir/f'projection_{calibration_seed}_{projection_seed}_{release_day}.sim',sim)

    return df, beta, calibration_seed, projection_seed, release_day
