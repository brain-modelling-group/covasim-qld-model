from celery import Celery
from covasim import misc
import outbreak

misc.git_info = lambda: None  # Disable this function to increase performance slightly

import os
broker = os.getenv('COVID_REDIS_URL','redis://127.0.0.1:6379')

# Create celery app
celery = Celery('outbreak')
celery.conf.broker_url = broker
celery.conf.result_backend = broker
celery.conf.task_default_queue = 'outbreak'
celery.conf.accept_content = ['pickle','json']
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'json'

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

    return sim_stats


