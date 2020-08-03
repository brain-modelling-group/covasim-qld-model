#!/bin/bash

COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"

if [ "$HOSTNAME" = athena ]; then
  export COVID_REDIS_URL="redis://apollo:6379"
  CONCURRENCY=24
elif [ "$HOSTNAME" = apollo ]; then
  export COVID_REDIS_URL="redis://apollo:6379"
  CONCURRENCY=20
else
  export COVID_REDIS_URL="redis://localhost:6379"
  CONCURRENCY=4
fi

celery -A outbreak.celery worker -l info -Q outbreak -Ofair --concurrency=${CONCURRENCY}
