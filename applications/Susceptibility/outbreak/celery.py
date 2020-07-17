from celery import Celery
from covasim import misc
import outbreak

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
celery.conf.result_serializer = 'json'
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_acks_late = True # Allow other servers to pick up tasks in case they are faster

@celery.task()
def run_australia_outbreak(seed, params, scen_policies):
    sim = outbreak.run_australia_outbreak(seed, params, scen_policies)

    # Returning the entire Sim results in too much disk space being consumed by the Redis backend
    # e.g. when running 1000 simulations. So instead, just keep summary statistics
    sim_stats = {}
    sim_stats['cum_infections'] = sim.results['cum_infections'][-1]
    sim_stats['cum_diagnoses'] = sim.results['cum_diagnoses'][-1]
    sim_stats['cum_deaths'] = sim.results['cum_deaths'][-1]
    sim_stats['cum_quarantined'] = sim.results['cum_quarantined'][-1]

    active_infections = sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values
    sim_stats['active_infections'] = active_infections[-1]
    sim_stats['peak_infections'] = max(sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values)
    sim_stats['peak_incidence'] = max(sim.results['new_infections'])

    return sim_stats


@celery.task()
def run_australia_test_prob(seed, params, scen_policies, symp_prob, asymp_prob, symp_quar_prob, asymp_quar_prob):
    sim = outbreak.run_australia_test_prob(seed, params, scen_policies, symp_prob, asymp_prob, symp_quar_prob, asymp_quar_prob)

    sim_stats = {}
    sim_stats['cum_infections'] = sim.results['cum_infections'][-1]
    sim_stats['cum_diagnoses'] = sim.results['cum_diagnoses'][-1]
    sim_stats['cum_deaths'] = sim.results['cum_deaths'][-1]
    sim_stats['cum_quarantined'] = sim.results['cum_quarantined'][-1]

    active_infections = sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values
    sim_stats['active_infections'] = active_infections[-1]
    sim_stats['peak_infections'] = max(sim.results['cum_infections'].values - sim.results['cum_recoveries'].values - sim.results['cum_deaths'].values)
    sim_stats['peak_incidence'] = max(sim.results['new_infections'])

    sim_stats['symp_prob'] = symp_prob
    sim_stats['asymp_prob'] = asymp_prob
    sim_stats['symp_quar_prob'] = symp_quar_prob
    sim_stats['asymp_quar_prob'] = asymp_quar_prob

    sim_stats['cum_tests'] = sim.results['cum_tests'][-1]

    return sim_stats