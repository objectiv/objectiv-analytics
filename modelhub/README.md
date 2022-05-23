# Open model hub

The open model hub consists of pre-built models and operations that you can combine to build advanced compound models with little effort. The open model hub is powered by [Bach](https://objectiv.io/docs/modeling/bach/), our python-based modeling library.

Visit [Objectiv Docs](https://objectiv.io/docs/modeling/open-model-hub/) to learn more

## Start modeling with Objectiv
If you want to use the open model hub, install the package from Pypi as follows:
```bash
pip install objectiv-modelhub
```
You are now ready to use the model hub. Either through your own notebooks/code or through our examples.

### Examples
We have some example notebooks in the 
[/notebooks/](https://github.com/objectiv/objectiv-analytics/tree/main/notebooks) directory of
the repository that demonstrate how you can work with the data in Python. These notebooks can run on _your_
collected data. The only thing that might need to be adjusted is how the connection to the database is 
made (see below). All other instructions live in the README.md in the link above.

### Your own code
To use the model hub in your own code, you can import the package and use it to get a Bach DataFrame 
([What is Bach?](https://www.objectiv.io/docs/modeling/bach/what-is-bach/)) to 
perform your operations on. The object can be instantiated as follows, where the `db_url` and `table_name`
should be adjusted depending on where the data is stored and how to access it.
```python
from modelhub import ModelHub
# instantiate the model hub
modelhub = ModelHub(time_aggregation='YYYY-MM-DD')
# get the Bach DataFrame to use with model hub models
df = modelhub.get_objectiv_dataframe(db_url='postgresql://user:pass@localhost:5432/database',
                                     table_name='data')
```

## Setup development environment
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


## Metabase integration

To enable Objectiv's Metabase integration, there are basically 2 steps:

### 1. Setup connectivity from Metabase to your database
   
Within Metabase, switch to admin mode, and select Databases to add your database (if this has not already been
done). Exit admin. 

Switching to the overview, in the section "our data" a new database, with the name of the database should be
present. If you select the database, a numeric ID will be in the URL, for example: 
"http://localhost:3000/browse/2-objectiv", in this case your database ID is 2.

The collection ID can be obtained in a similar way. From the overview page, select the collection (or create
one first) from "Our analytics". This will result in a URL like "http://localhost:3000/collection/2-objectiv",
in this case 2 is your collection ID.

Finally, if you have set up a dashboard, and want cards to be added to that automatically, open the dashboard;
the URL should be something like "http://localhost:3000/dashboard/1-model-hub", your dashboard ID is 1. This
is optional.

### 2. Configure Objectiv to communicate with Metabase. 

This works through exporting variables to the environment that is running bach. 
```
# This is the URL where the notebook can find Metabase. If the notebook is not running in Docker
# this will be the same as METABASE_WEB_URL
METABASE_URL="http://localhost:3000"

# this is the URL where the browser can find Metabase.
METABASE_WEB_URL="http://localhost:3000"

# username to login to Metabase. This use must have enough privileges to add/create cards
METABASE_USERNAME="demo@objectiv.io"
METABASE_PASSWORD="metabase1"

# id of added Database
METABASE_DATABASE_ID=2 # objectiv database

# id of collection
METABASE_COLLECTION_ID=2 # 2-objectiv

# id of dashboard to add cards to
METABASE_DASHBOARD_ID=1 # 1-model-hub
```
