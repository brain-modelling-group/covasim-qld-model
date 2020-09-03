from celery import Celery
from covasim import misc
import outbreak
import tqdm
import dill
import time
import sciris as sc
import numpy as np
import covasim as cv

misc.git_info = lambda: None  # Disable this function to increase performance slightly

import os

broker = os.getenv('COVID_REDIS_URL', 'redis://127.0.0.1:6379')

# Create celery app
celery = Celery('outbreak')
celery.conf.broker_url = broker
celery.conf.result_backend = broker
celery.conf.task_default_queue = 'outbreak'
celery.conf.accept_content = ['pickle', 'json']
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_acks_late = True # Allow other servers to pick up tasks in case they are faster

def stop_sim_scenarios(sim):
    # Stop a scenarios-type simulation after it exceeds 100 infections
    return (sim.t > 7 and np.sum(sim.results['new_infections'][sim.t-1]) > 100)

@celery.task()
def run_australia_outbreak(seed, params, scen_policies, people=None, popdict=None):

    with sc.Timer(label='Create simulation') as t:
        sim = outbreak.get_australia_outbreak(seed, params, scen_policies, people, popdict)

    with sc.Timer(label='Run simulation') as t:
        sim.run()

    if not sim.results_ready:
        sim.finalize()
        # Truncate the arrays
        for k, result in sim.results.items():
            if isinstance(result, cv.Result):
                result.values = result.values[0:sim.t+1]
            else:
                sim.results[k] = sim.results[k][0:sim.t+1]

    # Returning the entire Sim results in too much disk space being consumed by the Redis backend
    # e.g. when running 1000 simulations. So instead, just keep summary statistics
    sim_stats = {}
    sim_stats['end_day'] = sim.t

    sim_stats['cum_infections'] = sim.results['cum_infections'][-1]
    sim_stats['cum_diagnoses'] = sim.results['cum_diagnoses'][-1]
    sim_stats['cum_deaths'] = sim.results['cum_deaths'][-1]
    sim_stats['cum_quarantined'] = sim.results['cum_quarantined'][-1]

    active_infections = sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values
    sim_stats['active_infections'] = active_infections[-1]
    sim_stats['active_diagnosed'] = sum(sim.people.diagnosed & ~sim.people.recovered) # WARNING - this will not be correct if rescaling was used
    sim_stats['peak_infections'] = max(sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values)
    sim_stats['peak_incidence'] = max(sim.results['new_infections'])
    sim_stats['peak_diagnoses'] = max(sim.results['new_diagnoses'])

    sim_stats['symp_prob'] = params.test_prob['symp_prob']
    sim_stats['symp_quar_prob'] = params.test_prob['symp_quar_prob']
    sim_stats['test_delay'] = params.test_prob['test_delay']
    sim_stats['swab_delay'] = params.test_prob['swab_delay']
    sim_stats['test_isolation_compliance'] = params.test_prob['test_isolation_compliance']
    sim_stats['cum_tests'] = sim.results['cum_tests'][-1]

    new_infections = np.where(sim.results['new_infections'])[0]
    new_diagnoses = np.where(sim.results['new_diagnoses'])[0]
    if len(new_diagnoses) and len(new_infections):
        sim_stats['time_to_first_diagnosis'] = new_diagnoses[0]-new_infections[0] # Time to first diagnosis
    else:
        sim_stats['time_to_first_diagnosis'] = None

    if len(new_diagnoses):
        # If there was at least one diagnosis
        sim_stats['cum_infections_at_first_diagnosis'] = sim.results['cum_infections'][new_diagnoses[0]]
    else:
        sim_stats['cum_infections_at_first_diagnosis'] = None

    sim_stats['r_eff7'] = np.average(sim.results['r_eff'][-7:]) # R_eff over last 7 days

    return sim_stats


@celery.task()
def run_sim(sim, seed, analyzer_string=None):
    """
    Run a generic Sim

    It's possible to quickly run out of storage space if thousands of Sims are stored with all of
    their people. Instead, can trivially run the simulation and have a pickleable analyzer function
    for postprocessing
    Args:
        sim:
        seed:
        analyzer:

    Returns:

    """

    # The sim should not be initialized
    sim.pars['rand_seed'] = seed
    sim.run()

    analyzer = dill.loads(analyzer_string)

    if analyzer is None:
        return sim
    else:
        return analyzer(sim)

def run_multi_sim(sim, n_runs, celery=True, analyzer=None):

    from .celery import run_sim
    from celery import group

    analyzer_string = dill.dumps(analyzer)

    if celery:
        # Run simulations using celery
        job = group([run_sim.s(sim=sim, seed=i, analyzer_string=analyzer_string) for i in range(n_runs)])
        result = job.apply_async()

        with tqdm.tqdm(total=n_runs) as pbar:
            while result.completed_count() < n_runs:
                time.sleep(1)
                pbar.n = result.completed_count()
                pbar.refresh()
            pbar.n = result.completed_count()
            pbar.refresh()
        output = result.join()
        result.forget()

    else:
        output = []
        for i in tqdm.tqdm(range(n_runs)):
            output.append(run_sim(sim=sc.dcp(sim), seed=i, analyzer_string=analyzer_string))

    return output