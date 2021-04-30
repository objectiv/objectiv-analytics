
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
 

To feed the endpoint test data, run something like this:
```bash
cat sample_data/objectiv.ai/user-journey-3.json5 | curl  -X  POST  -H "Content-Type: application/data" --data-binary @- http://127.0.0.1:5000/
```

To load a lot of data continuously:
```bash
while true;
  do cat sample_data/objectiv.ai/user-journey-3.json5 | curl  -X  POST  -H "Content-Type: application/data" --data-binary @- http://127.0.0.1:5000/;
  sleep 0.1;
done
```

# Run DBT models
```bash
cd data_models
dbt run --profiles-dir .  
```

if all is well, the journey should validate, and result in a json file in `jsons/OK/`

## Run validation on file with events:
### Alternative 1: Python Validator
```bash
python objectiv_backend/schema/validate_events.py sample_data/objectiv.ai/user-journey-1.json5

# Or with custom event and context schema extensions:
python objectiv_backend/schema/validate_events.py \
  --schema-extension-context sample_data/extension_demo/extension_1/schema_extension_context.json \
  --schema-extension-event sample_data/extension_demo/extension_1/schema_extension_event.json \
  sample_data/objectiv.ai/user-journey-*.json5
```
### Alternative 1: Use JSON Schema validator
```bash
# First generate a JSON schema from our event-schema
python objectiv_backend/schema/generate_json_schema.py > test_schema.json
# Validate a json5 file using the generate JSON schema.
python tools/json5schema.py -i sample_data/objectiv.ai/user-journey-1.json5 test_schema.json

# To run against all examples of wrong data
for f in sample_data/test_data_invalid/*.json5;
  do python tools/json5schema.py -i $f test_schema.json; echo $? - $f;
done

```

# Build
Make sure the python `build` package is installed.
Note: on Ubuntu this might give some annoying warnings about a keyring, the escape button seems the right
response to those.
```
apt install python3-venv
pip install build
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
