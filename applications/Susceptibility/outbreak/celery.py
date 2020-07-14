from celery import Celery
from covasim import misc
import outbreak

misc.git_info = lambda: None  # Disable this function to increase performance slightly

# Create celery app
celery = Celery('outbreak')
celery.conf.broker_url = "redis://127.0.0.1:6379"
celery.conf.result_backend = "redis://127.0.0.1:6379"
celery.conf.task_default_queue = 'outbreak'
celery.conf.accept_content = ['pickle']
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'

@celery.task()
def run_australia_outbreak(seed, params, scen_policies):
    return outbreak.run_australia_outbreak(seed, params, scen_policies)
