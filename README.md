# Running the demo

Running the dev stack, containerized, is a fairly simple process, involving 2 steps:

0. First build ROD, see `objectiv-demo` for info

1. Build the images (required for running the dev stack):

```bash
make build-all-images
```

By default, all images will be tagged `latest`. This can be overridden by setting 
`TAG`.

2. Starting the containers:
```bash
make start
```

To stop a running stack, simply run:
```bash
make stop
```

## Tips 'n tricks
Some useful tricks are here

### What about PG configuration and permissions?
As this is a demo environment, permissions are pretty simple; the credentials are set in 
`docker/pg_env` and imported into the containers that need them.

### What services are where?
Typically everything is available on localhost:
- rod (http://localhost:3000)
- notebook (http://localhost:8080)

### Connecting to Notebook
By default, you need a token to connect to the Jupyter Notebook. You can find it in
the logs like so:
```bash
docker logs objectiv_notebook 2>&1|grep http.*token\=
```

### start part of the stack
It's also possible to only start parts of the stack. For example, to only run the collector; run:

```bash
docker-compose up collector
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


