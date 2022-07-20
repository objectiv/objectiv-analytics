# Open model hub

The [open model hub](https://objectiv.io/docs/modeling/open-model-hub/) is a toolkit with functions and models 
that can run directly on a full dataset collected with Objectiv's Tracker SDKs. All models are open-source, 
free to use, and can easily be combined to build advanced compound models.

## How to use the open model hub

Three types of functions/models are provided:
1. [Helper functions](https://objectiv.io/docs/modeling/open-model-hub/models/helper-functions/): 
  simplify manipulating and analyzing the data.
2. [Aggregation models](https://objectiv.io/docs/modeling/open-model-hub/models/aggregation/): 
  enable running some of the more common data analyses and product analytics metrics.
3. [Machine learning models](https://objectiv.io/docs/modeling/open-model-hub/models/machine-learning/).

Modeling behavior of users and groups is enabled through configurable
[Identity Resolution](https://objectiv.io/docs/modeling/open-model-hub/identity-resolution/).

See how to [get started in your notebook](https://objectiv.io/docs/modeling/get-started-in-your-notebook/) 
and the [example notebooks](https://objectiv.io/docs/modeling/example-notebooks/), and install the 
model hub package directly from PyPI:

```console
pip install objectiv-modelhub
```

## Powered by Bach
The open model hub is powered by [Bach](https://objectiv.io/docs/modeling/bach/): Objectiv’s data modeling 
library. With Bach, you can compose models with familiar Pandas-like dataframe operations that use an SQL 
abstraction layer to run on the full dataset. Models can be output to SQL with one command.

## Example notebooks
We have some example notebooks in the 
[/notebooks/](https://github.com/objectiv/objectiv-analytics/tree/main/notebooks) directory of
the repository that demonstrate how you can work with the data in Python. These notebooks can run on _your_
collected data. The only thing that might need to be adjusted is how the connection to the database is 
made (see below). All other instructions live in the README.md in the link above.


## Set up development environment
This section is only required for development on the objectiv-modelhub package.

```bash
virtualenv venv
source venv/bin/activate
export PYTHONPATH=.

# You probably want to remove objectiv-modelhub if you did not just create a fresh venv
pip uninstall objectiv-modelhub

# This will fail if the postgres lib development headers are not present if so, then on Ubuntu that can
# be fixed with: sudo apt-get install libpq-dev
pip install -r requirements.txt

# in case your notebook can not find all of the packages you just installed
# you may also need to create a kernel config for this venv:

ipython kernel install --user --name=objectiv_venv
# now restart the notebook server, and from the kernel menu select 'objectiv_venv'
```

### PyCharm
* Mark the following directories as "Sources root":
   1. `/bach/`
   2. `/modelhub/`
* Set `modelhub/venv/bin/python` as the default interpreter for the project
