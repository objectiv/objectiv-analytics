# Configuration Options
All configuration options are set through environment variables.

## 1. Input Configuration

There is currently one variable supported for configuring the data input format:

- `SCHEMA_EXTENSION_DIRECTORY` - A directory with schema extension files. Each schema extension is a json file that described part
of the full schema. **TODO:** link to a schema explanation.
If not set the default schema is used.


## 2. Output Configuration
Currently, the only supported non-experimental output option for the collector is Postgres.

Postgres variables:
- `PG_HOSTNAME`      - Default: `localhost`
- `PG_PORT`          - Default: `5432`
- `PG_DATABASE_NAME` - Default: `objectiv`
- `PG_USER`          - Default: `objectiv`
- `PG_PASSWORD`

## Experimental Configuration Options
There are some additional experimental configuration options. These are not (yet) supported and might be
subject to change in the future. See `config.py` if you wish to use those.
