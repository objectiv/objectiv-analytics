.. _example_machine_learning:

.. frontmatterposition:: 1

.. currentmodule:: bach

================
Bach and sklearn
================

With Objectiv you can do all your analysis and Machine Learning directly on the raw data in your SQL database.
This example shows in the simplest way possible how you can use Objectiv to create a basic feature set and use
sklearn to do machine learning on this data set. We also have an example that goes deeper into
feature engineering :ref:`here <example_feature_engineering>`.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/sklearn-example.ipynb>`_
to run on your own data or use our
`quickstart
<https://objectiv.io/docs/home/quickstart-guide/>`_ to try it out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

This object points to all data in the data set. Without any aggregation, this dataset is too large to
for pandas and sklearn. For the data set that we need, we aggregate to user level, at which point it is
small enough to fit in memory.

We create a data set of per user all the root locations that the user clicked on.

.. code-block:: python

    # extract the root location from the location stack
    df['root'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')

    # root series is later unstacked and its values might contain dashes
    # which are not allowed in BigQuery column names, lets replace them
    df['root'] = df['root'].str.replace('-', '_')

    # only look at press events and count the root locations
    features = df[(df.event_type=='PressEvent')].groupby('user_id').root.value_counts()
    # unstack the series, to create a DataFrame with the number of clicks per root location as columns
    features_unstacked = features.unstack(fill_value=0)

Now we have a basic feature set that is small enough to fit in memory. This can be used with sklearn, as we
demonstrate in this example.

.. code-block:: python

    from sklearn import cluster

    # export to pandas now
    pdf = features_unstacked.to_pandas()

    # do the clustering using the pandas DataFrame and set the labels as a column to that DataFrame
    est = cluster.KMeans(n_clusters=3)
    est.fit(pdf)
    pdf['cluster'] = est.labels_

Now you can use the created clusters on your entire data set again if you add it back to your DataFrame.
This is simple, as Bach and pandas are cooperating nicely. Your original Objectiv data now has a 'cluster'
column.

.. code-block:: python

    features_unstacked['cluster'] = pdf['cluster']
    df_with_cluster_results = df.merge(features_unstacked[['cluster']], on='user_id')

You can use this column, just as any other. For example you can now use your created clusters to group models
from the model hub by:

.. code-block:: python

    modelhub.agg.session_duration(df_with_cluster_results, groupby='cluster').head()
    # Expected output:
    # cluster
    # 0   0 days 00:09:18.204353
    # 1   0 days 00:10:25.104636
    # 2   0 days 00:20:43.561232
    # Name: session_duration, dtype: timedelta64[ns]
