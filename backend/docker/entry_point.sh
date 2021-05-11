#!/bin/bash

# Depending on environment variables this script will do one of two things:
# 1. Run a collector instance, i.e. bind to port 5000 and accept event data
# 2. Run an objectiv worker, i.e. process data on the queues and write the result to the database.
#
# By default option 1 happens. Only if ASYNC_MODE=true and ASYNC_WORK_TYPE=worker does option two happen
#

if [[ "$ASYNC_MODE" == "true" && "$ASYNC_WORKER_TYPE" == "worker" ]]; then
  echo "starting worker"
  objectiv-workers all --loop
  exit 0
fi;

# Tell python not to buffer any output to stdout and stderr. Not setting this makes any debugging almost
# impossible
export PYTHONUNBUFFERED=1

echo "starting gunicorn"
# Run gunicorn. $USER and $PORT are set in the Dockerfile
exec gunicorn --config /etc/gunicorn.conf.py \
--bind 0.0.0.0:5000 \
--access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(l)s' \
--user www-data \
objectiv_backend.wsgi
