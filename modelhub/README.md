# Objectiv Analysis

## Start modeling with Objectiv
Clone this repository and install the following packages with `pip install -e` from the root of the
repository. The Bach package requires a local installation of postgres.
```bash
pip install -e bach
pip install -e modelhub
```

You can now import the package and work with your data in a Jupyter notebook. This can be done with the
ObjectivFrame object. The object can be instantiated as follows, where the `db_url` and `table_name`
should be adjusted depending on where the data is stored and how to access it.
```python
from modelhub import ModelHub
# instantiate the model hub
modelhub = ModelHub(time_aggregation='YYYY-MM-DD')
# get the Bach DataFrame to use with model hub models
df = modelhub.get_objectiv_dataframe(db_url='postgresql://user:pass@localhost:5432/database',
                                     table_name='data')
```

We have two notebooks in the 
[/notebooks/](https://github.com/objectiv/objectiv-analytics/tree/main/notebooks) folder of
the repository that demonstrate how you can work with the data in Python. Both notebooks can run on _your_
collected data. The only thing that might need to be adjusted is how the connection to the database is made
for the instantiation of the ObjectivFrame object (as per above).

### The open taxonomy how-to notebook ([open-taxonomy-how-to.ipynb](https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/open-taxonomy-how-to.ipynb))
This notebook demonstrates the contents and structure of the data in an interactive way. Also shows how you
can work with the using Bach, our pandas inspired interface that works directly with your data in the
database. The full reference of Bach is found [here](https://objectiv.io/docs/modeling/reference/).

### Model Hub demo notebook ([model-hub-demo-notebook.ipynb](https://github.com/objectiv/objectiv-analytics/blob/main/analysis/model-hub-demo-notebook.ipynb))
This notebook shows how you can work with the data using standard models from the model hub. For the
conversion models to give sensible results the `add_conversion_event` paramaters need to be adjusted to your
own data. The full model hub reference is found
[here](https://objectiv.io/docs/modeling/Objectiv/modelhub.ModelHub/). The Metabase example is made
to work with our [quickstart demo](https://objectiv.io/docs/home/quickstart-guide/), in which Metabase is included.
See the section at the end of this readme for how to set up Metabaser integration for your data.

## Setup development environment
This section is only required for development of the bach and open taxonomy packages. 

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

### PyCharm
* Mark the following directories as "Sources root":
   1. `/bach/`
   2. `/modelhub/`
* Set `analysis/venv/bin/python` as the default interpreter for the project


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
