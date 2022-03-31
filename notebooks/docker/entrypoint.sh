#!/bin/bash

set -e


# wait a bit to give PG a chance to start up
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "${POSTGRES_HOSTNAME}" -U "${POSTGRES_USER}" -c '\q'; do
  >&2 echo "Postgres is not yet available - sleeping 1s"
  sleep 1
done
  
>&2 echo "Postgres is up - executing command"

for sql in /services/*.sql
do
  echo "Loading data from $sql into $POSTGRES_HOSTNAME/$POSTGRES_DB"
  cat $sql | psql -U $POSTGRES_USER -h $POSTGRES_HOSTNAME $POSTGRES_DB
done

# load virtualenv
source /services/venv/bin/activate

# db connection paramaters
export DSN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOSTNAME}/${POSTGRES_DB}"

# start notebook
# disable TOKEN
export JUPYTER_TOKEN=objectiv
jupyter lab --notebook-dir /services/notebooks --no-browser --ip 0.0.0.0
