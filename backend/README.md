
# Development
## Setup
```bash
virtualenv venv
source venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:.
export FLASK_APP=objectiv_backend.app
# the following command fails if the postgres lib development headers are not present
# if so, then on ubuntu that can be fixed with: sudo apt-get install libpq-dev
pip install --require-hashes -r requirements.txt
pip install -r requirements-dev.txt
```

## Start DB
```bash
cd ..; docker-compose up --detach postgres
cd backend; python objectiv_backend/tools/db_init/db_init.py
```
SECURITY WARNING: The above docker-compose command starts a postgres container that allows connections
without verifying passwords. Do not use this in production or on a shared system!
## Run Collector
After setting up the python env, simply run:
```bash
flask run
```
Start worker that will process events that flask will add to the queue:
```bash
python objectiv_backend/workers/worker.py all --loop
```
 
## Run validation on file with events:
### Alternative 1: Python Validator
```bash
python objectiv_backend/schema/validate_events.py <path to json file with events>
```

### Alternative 1: Use JSON Schema validator
```bash
# First generate a JSON schema from our event-schema
python objectiv_backend/schema/generate_json_schema.py > test_schema.json
# Validate a json5 file using the generate JSON schema.
python -m jsonschema -i <path to json file with events> test_schema.json
```

## Run tests
```bash
pytest tests
```

# Build
## Build Container Image
Only requires docker, no python.
```
make docker-image
```

## Build Python Package
Requires additional python packages installed: `build` and `virtualenv`
```bash
pip install -r build-requirements.txt
```

Build python package:
```bash
make clean
make python-package
```


# Allowed schema extensions
TODO: update this, and move it to some docs specifically about the taxonomy
* Events:
    * adding new events
    * adding parents to an existing event
    * adding contexts to the requiresContext field of an existing event
* Contexts:
    * adding new contexts
    * adding parents to an existing context
    * adding properties to an existing context
    * adding sub-properties to an existing context (e.g. a "minimum" field for an integer)
