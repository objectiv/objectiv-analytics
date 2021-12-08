# Objectiv Analysis
For now this readme is focussed on development. We'll replace this by an end-user targeted readme later on.

## Setup
```bash
virtualenv venv
source venv/bin/activate
export PYTHONPATH=.

# This will fail if the postgres lib development headers are not present if so, then on Ubuntu that can
# be fixed with: sudo apt-get install libpq-dev
pip install -r requirements.txt

# in case your notebook can not find all of the packages you just installed
# you may also need to create a kernel config for this venv:

ipython kernel install --user --name=objectiv_venv
# now restart the notebook server, and from the kernel menu select 'objectiv_venv'

```

## PyCharm
* Mark the following directories as "Sources root":
   1. `/bach/`
   2. `/analysis/bach_open_taxonomy/`
* Set `analysis/venv/bin/python` as the default interpreter for the project
