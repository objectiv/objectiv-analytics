
# Development Setup
## Setup
```bash
virtualenv venv
source venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:.
export FLASK_APP=objectiv_backend.app
# the following command fails if the postgres lib development headers are not present
# if so, then on ubuntu that can be fixed with: sudo apt-get install libpq-dev
pip install -r requirements.txt
```

## Start DB
```bash
cd ..; docker-compose up --detach postgres
```
## Run flask endpoint
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

# Build
Make sure the python `build` and `virtualenv` packages are installed.
```bash
pip install build virtualenv
```

Build python package and docker image:
```bash
make clean
make
```


# Allowed schema extensions
* Events:
    * adding new events
    * adding parents to an existing event
    * adding contexts to the requiresContext field of an existing event
* Contexts:
    * adding new contexts
    * adding parents to an existing context
    * adding properties to an existing context
    * adding sub-properties to an existing context (e.g. a "minimum" field for an integer)
