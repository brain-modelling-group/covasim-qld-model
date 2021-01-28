#!/bin/bash

# Run celery worker processes

COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"

if [ "$HOSTNAME" = athena ]; then
  export COVID_REDIS_URL="redis://apollo:6379"
  CONCURRENCY=50
elif [ "$HOSTNAME" = apollo ]; then
  export COVID_REDIS_URL="redis://apollo:6379"
  CONCURRENCY=40
else
  export COVID_REDIS_URL="redis://localhost:6379"
  CONCURRENCY=4
fi

celery -A outbreak.celery worker -l info -Q outbreak -Ofair --concurrency=${CONCURRENCY}
