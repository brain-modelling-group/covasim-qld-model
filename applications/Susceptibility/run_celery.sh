#!/bin/bash

COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"
export COVID_REDIS_URL="redis://apollo:6379"
celery -A outbreak.celery worker -l info -Q outbreak -Ofair --concurrency=30
