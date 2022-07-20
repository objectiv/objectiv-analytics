.. _example_feature_engineering:

.. frontmatterposition:: 5

.. currentmodule:: bach

=============================
Feature engineering with Bach
=============================

This example shows how Bach can be used for feature engineering. We'll go through describing the data, finding
outliers, transforming data and grouping and aggregating data so that a useful feature set is created that
can be used for machine learning. We have a separate example available that goes into the details of how a
data set prepared in Bach can be used for machine learning with sklearn 
:doc:`here <machine-learning>`.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/feature-engineering.ipynb>`_
to run on your own data or use our `quickstart <https://objectiv.io/docs/home/quickstart-guide/>`_ to try it 
out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

This object points to all data in the data set. Too large to run in pandas and therefore sklearn. For the
data set that we need, we aggregate to user level, at which point it is small enough to fit in memory.

We start with showing the first couple of rows from the data set and describing the entire data set.

.. code-block:: python

    df.head()

Columns of interest are 'user_id', this is what we will aggregate to. 'moment' contains timestamp info for the
events. :ref:`global_contexts` and the :ref:`location_stack` contain most of the event specific data.

.. code-block:: python

    df.describe(include='all').head()


Creating a feature set
----------------------
We'd like to create a feature set that describes the behaviour of users in a way. We start with extracting
the root location from the location stack. This indicates what parts of our website users have visited. Using
`to_numpy()` shows the results as a numpy array.

.. code-block:: python

    df['root'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
    # root series is later unstacked and its values might contain dashes
    # which are not allowed in BigQuery column names, lets replace them
    df['root'] = df['root'].str.replace('-', '_')
    df.root.unique().to_numpy()

`['jobs', 'docs', 'home'...]` etc is returned, the sections of the objectiv.io website.

Check missing values
--------------------
.. code-block:: python

    df.root.isnull().value_counts().head()

A quick check learns us that there are no missing values to worry about. Now we want a data set with
interactions on our different sections, in particular, presses. This is an event type. We first want an
overview of the different event types that exist and select the one we are interested in.

.. code-block:: python

    df.event_type.unique().to_numpy()

We are interested in 'PressEvent'.

Creating the variables
----------------------
The next code block shows that we select only press events and then group
by 'user_id' and 'root' and count the session_hit_number. After that the results are unstacked, resulting in
a table where each row represents a user (the index is 'user_id') and the columns are the different root
locations and its values are the number of times a user clicked in that sections.

.. code-block:: python

    features = df[(df.event_type=='PressEvent')].groupby(['user_id','root']).session_hit_number.count()
    features_unstacked = features.unstack()
    features_unstacked.head()

Fill empty values
-----------------
Now we do have empty values, so we fill them with 0, as empty means that the user did not click in the
section.

.. code-block:: python

    features_unstacked = features.unstack(fill_value=0)

Describe the data set
---------------------
We use describe again to get an impression of out created per-user data set.

.. code-block:: python

    features_unstacked.materialize().describe().head()

Looking at the mean, some sections seem to be used a lot more than others. Also the max
number of clicks seems quite different per root section. This information can be used to drop some of the
variables from our data set or the use scaling or outlier detection. We will plot histograms for the

Visualize the data
------------------
.. code-block:: python

    from matplotlib import pyplot as plt
    import math

    figure, axis = plt.subplots(math.ceil(len(features_unstacked.data_columns)/4), 4, figsize=(15,10))

    for idx, name in enumerate(features_unstacked.data_columns):
        features_unstacked[[name]].plot.hist(bins=5, title=name, ax=axis.flat[idx])
    plt.tight_layout()

The histograms show that indeed the higher values seem quite anomalous for most of the root locations. This
could be a reason to drop some of these observations or resort to scaling methods. For now we continue with
the data set as is.

Add time feature
----------------
Now we want to add some time feature to our data set. We add the average session length per user to the data
set. We can use the model hub for this. `fillna` is used to fill missing values.

.. code-block:: python

    import datetime
    features_unstacked['session_duration'] = modelhub.agg.session_duration(df, groupby='user_id').fillna(datetime.timedelta(0))

Export to pandas for sklearn
----------------------------
Now that we have our data set, we can use it for machine learning, using for example sklearn. To do so
we call `to_pandas()` to get a pandas DataFrame that can be used in sklearn.

.. code-block:: python

    pdf = features_unstacked.to_pandas()

