#!/bin/sh

. venv/bin/activate
export PYTHONPATH=.:$PYTHONPATH
# Tell python not to buffer any output to stdout and stderr. Not setting this makes any debugging almost
# impossible
export PYTHONUNBUFFERED=1

# Run gunicorn. $USER and $PORT are set in the Dockerfile
exec gunicorn --config /etc/gunicorn.conf.py \
--bind 0.0.0.0:5000 \
--access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(l)s' \
--user www-data \
objectiv_backend.wsgi
