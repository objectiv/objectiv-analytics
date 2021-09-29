# Objectiv Analytics
Objectiv Analytics enables you to track and collect events from your product and analyse the collected data
with powerful models. The collected data follows a standardized taxonomy, which enable many advanced
analysis out of the box. If needed, both the data taxonomy and the data models can be easily extended.

Objectiv is fully open source, and easy to host yourself; so no need to share your customers's sensitive
data with anyone.

More information about what Objectiv Analytics is, and how it compares to other analytics solution can be
found on https://objectiv.io

We also created a demo app that shows how easy it is to integrate the Objectiv Analytics tracker into an
app, and that gives an idea about what the resulting data insights look like.
See the [objectiv-demo repository](https://github.com/objectiv/objectiv-demo).


## Using Objectiv
Starting to use Objectiv Analytics is not hard:
1. Integrate the Objectiv-tracker into your app.
2. Run an Objectiv Pipeline backend to receive and process the data.

## Quick Start
### Quick Start: Run Objectiv Pipeline Dockerized
This is a great way to run Objectiv locally and to see what it is about. With some additional work this
setup can also be used for low-traffic sites and apps. See also
[Running the Objectiv Pipeline in Production](#running-the-objectiv-pipeline-in-production)


The below commands assume that you have `docker-compose` [installed](https://docs.docker.com/compose/install/).
```bash
docker-compose pull  # pull pre-built images from gcr
docker-compose up    # spin up Objective pipeline
```
This will spin up three images:
* `objectiv_collector` - Endpoint that the Objectiv-tracker can send events to (http://localhost:5000).
* `objectiv_postgres` - Database to store data.
* `objectiv_notebook` - Jupyter notebook that can be used to query the data (http://localhost:8888).

SECURITY WARNING: The above docker-compose commands start a postgres container that allows connections
without verifying passwords. Do not use this in production or on a shared system!

### Quick Start: Integrate the Objectiv-Tracker in your app
TODO



## Objectiv Architecture
The following diagram shows in the Objectiv architecture in a nutshell. There are four main components:
1. The Objectiv tracker. You'll need to integrate this into your project.
   This is similar to e.g. a Google Analytics tracker.
   The code for this can be found in the `tracker` directory. 
   See [tracker/README.md](tracker/README.md) for more information
2. The Objectiv collector. A python app, which can be found in the `backend` directory.
   See [backend/README.md](backend/README.md) for more information
3. The database is used to store raw data, as well as processed data. We use SQL-supporting database,
   because SQL is a very powerful query standard, and databases nowadays can process huge amounts of data.
   Currently we only support Postgres. In the future we'll also support popular hosted big-data solutions.
4. The Objectiv models. TODO


```
    |=[Your App]==============|
    |                         |
    |  [1. Objectiv Tracker]  |
    |      ||                 |
    |======||=================|
           ||
           ||
    |======||=======[Objectiv Pipeline]====================================|
    |      \/                                                              |
    |  |===============================|                                   |
    |  |      [2. Objectiv Collector]  |                                   |
    |  |===============================|                                   |
    |      ||                                                              |
    |  |===||=================================|                            |
    |  |   \/     [3. Database]               |                            |
    |  |  ____________      _______________   |     ____________           |
    |  |  |raw events|      |analysis data| ======> | Insights |           |
    |  |  ------------      ---------------   |     ------------           |
    |  |===||================/\==||===========|                            |
    |      ||                ||  ||                                        |
    |      \/                ||  \/                                        |
    |  |===============================|                                   |
    |  |      [4. Objectiv Models]     |                                   |
    |  |===============================|                                   |
    |======================================================================|
```
For more information on the Objectiv architecture see TODO.


## Building Container Images
Requirements:
* make
* docker
```bash
make all
```

By default all images will be tagged with `latest`.

## Running Contain Images Locally
By default the docker-compose file will try to get images from our container registry. By setting 
`OBJECTIV_CONTAINER_URL` we can tell it to use local images.

```console
OBJECTIV_CONTAINER_URL=objectiv
docker-compose up
```

## Running the Objectiv Pipeline in Production
TODO
This is quite straightforward. See TODO.



## Tips 'n tricks
Some useful tricks are here

### What about PG configuration and permissions?
As this is a demo environment, permissions are pretty simple; the credentials are set in 
`docker/pg_env` and imported into the containers that need them.

### Connecting to Notebook
By default, you need a token to connect to the Jupyter Notebook. You can find it in
the logs like so:
```bash
docker logs objectiv_notebook 2>&1|grep http.*token\=
```

### start part of the stack
It's also possible to only start parts of the stack. For example, to only run the collector; run:

```bash
docker-compose up objectiv_collector
```

This will start the collector, and any dependencies it has (eg. postgres).

### Query the DB
To connect to the running DB, simply execute:
```bash
docker exec -ti objectiv_postgres psql -U objectiv
```

or by using a local client:
```bash
psql -U objectiv -h 127.0.0.1
```

### DB initialisation / persistence
At the first start-up, postgres will be initialised. This means a db will be created. As 
this is persisted on disk (in a docker volume), on subsequent startups, the persisted db 
will be loaded. In case of DB changes, this may cause problems. use 

```bash
docker volume list
``` 
to check if there are any existing volumes on disk, and remove them before starting up 
the stack with db changes, to make sure the DB is properly initialised. The volume used by
PG is called pgdata. To remove it, lookup the name from the list and run:
```bash
docker volume rm <volumename>
```

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md)
