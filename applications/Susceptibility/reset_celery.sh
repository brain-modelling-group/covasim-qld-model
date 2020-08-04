#!/bin/bash

# Delete any lingering jobs in the Celery queue
COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"
export COVID_REDIS_URL="redis://apollo:6379"
celery -A outbreak.celery purge
