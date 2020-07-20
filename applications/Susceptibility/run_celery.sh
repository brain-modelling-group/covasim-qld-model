#!/bin/bash

COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"
export COVID_REDIS_URL="redis://127.0.0.1:6379"
celery -A outbreak.celery worker -l info -Q outbreak -Ofair --concurrency=4
