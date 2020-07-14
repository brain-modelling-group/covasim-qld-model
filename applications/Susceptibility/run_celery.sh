#!/bin/bash

COVADIR="$(dirname $(dirname $(dirname $(realpath $0))))"
export PYTHONPATH="${PYTHONPATH}:${COVADIR}"

celery -A outbreak.celery worker -l info -Q outbreak
