.. _example_product_analytics:

.. frontmatterposition:: 2

.. currentmodule:: bach_open_taxonomy

=======================
Basic product analytics
=======================

This example shows how the open model hub can be used for basic product analytics.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/basic-product-analytics.ipynb>`_
to run on your own data or use our
`quickstart
<https://objectiv.io/docs/home/quickstart-guide/>`_ to try it out with demo data in 5 minutes.

At first we have to install the open model hub and instantiate the Objectiv DataFrame object. See
:ref:`getting_started_with_objectiv` for more info on this. The data used in this example is
based on the data set that comes with our quickstart docker demo.

First we look at the data.

.. code-block:: python

    df.sort_values('session_id', ascending=False).head()

The columns 'global_contexts' and the 'location_stack' contain most of the event specific data. These columns
are json type columns and we can extract data from it based on the keys of the json objects using
:doc:`get_from_context_with_type_series <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.objectiv>`. 
Or use methods specific to the :ref:`location_stack` or :ref:`global_contexts` to extract the data.


.. code-block:: python

    df['application'] = df.global_contexts.gc.application
    df['feature_nice_name'] = df.location_stack.ls.nice_name
    df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
    df['referrer'] = df.global_contexts.gc.get_from_context_with_type_series(type='HttpContext', key='referrer')
    # add marketing context as columns
    df['utm_source'] = df.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='source')
    df['utm_medium'] = df.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='medium')
    df['utm_campaign'] = df.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='campaign')
    df['utm_content'] = df.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='content')
    df['utm_term'] = df.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='term')

Now we will go though a selection of basic analytics metrics. We can use models from the :ref:`models
<models>`
for this purpose or use :ref:`Bach <bach>` to do data analysis directly on the data stored in the SQL database using 
pandas-like syntax.

For each example, `head()`, `to_pandas()` or `to_numpy()` can be used to execute the generated SQL and get
the results in your notebook.

Unique users
------------
The `daily_users` uses the `time_aggregation` as set when the model hub was instantiated. In this case
`time_aggregation` was set to 'YYYY-MM-DD', so the aggregation is daily. For `monthly_users`, the
default time_aggregation is overridden by using a different `groupby`.

.. code-block:: python

    daily_users = modelhub.aggregate.unique_users(df)
    montly_users = modelhub.aggregate.unique_users(df, groupby=modelhub.time_agg(df, 'YYYY-MM'))
    users_root = modelhub.aggregate.unique_users(df, groupby=['application', 'root_location'])

User time spent
---------------
Similarly we can calculate the average session duration for time intervals. `duration_root_month` gives the
average time spent per root location per month.

.. code-block:: python

    duration_daily = modelhub.aggregate.session_duration(df)
    duration_monthly = modelhub.aggregate.session_duration(df, groupby=modelhub.time_agg(df, 'YYYY-MM'))
    duration_root_month = modelhub.aggregate.session_duration(df, groupby=['root_location', modelhub.time_agg(df, 'YYYY-MM')])

This example shows the quartiles of time spent. Materialization is needed because the expression of the
created series contains aggregated data, and it is not allowed to aggregate that.

.. code-block:: python

    session_duration = modelhub.aggregate.session_duration(df, groupby='session_id', exclude_bounces=False)
    session_duration.to_frame().materialize()['session_duration'].quantile(q=[0.25, 0.50, 0.75]).head()

Top used features
-----------------

.. code-block:: python

    # select only user actions, so stack_event_types must be a superset of ['InteractiveEvent']
    interactive_events = df[df.stack_event_types>=['InteractiveEvent']]

    # users by feature
    users_feature = interactive_events.groupby(['application', 'feature_nice_name', 'event_type']).agg({'user_id':'nunique'})
    users_feature.sort_values('user_id_nunique', ascending=False).head()

Most used product areas
-----------------------

First we use the model hub to get the unique users per application, root location, feature, and event type.
From this prepared dataset, we show the users for the home page first.

.. code-block:: python

    most_interactions = modelhub.agg.unique_users(interactive_events, groupby=['application','root_location','feature_nice_name', 'event_type'])
    most_interactions = most_interactions.to_frame().reset_index()

    home_users = most_interactions[(most_interactions.application == 'objectiv-website') &
                                   (most_interactions.root_location == 'home')]
    home_users.sort_values('unique_users', ascending=False).head()

From the same `most_interactions` object, we can select the top interactions for the 'docs' page.

.. code-block:: python

    docs_users = most_interactions[most_interactions.application == 'objectiv-docs']
    docs_users.sort_values('unique_users', ascending=False).head()

User origin
-----------

.. code-block:: python

    # users by referrer
    modelhub.agg.unique_users(df, groupby='referrer').sort_values(ascending=False).head()

Marketing
---------
Calculate the number of users per campaign.

.. code-block:: python

    modelhub.agg.unique_users(df, groupby=['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'])

Look at top used features by campaign, using the previously created interactive_events to focus just on user
interactions.

.. code-block:: python

    modelhub.agg.unique_users(interactive_events, groupby=['utm_source', 'utm_term', 'feature_nice_name', 'event_type'])

Conversions
-----------
First we define a conversion event in the Objectiv DataFrame.

.. code-block:: python

    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'id': 'objectiv-on-github',
                                                                         '_type': 'LinkContext'}:].fillna(
                                                 df.location_stack.json[{'id': 'github', '_type': 'LinkContext'}:]),
                                  event_type='PressEvent',
                                  name='github_press')

This can be used by several models from the model hub using the defined name ('github_press'). First we calculate
the number of unique converted users.

.. code-block:: python

    df['is_conversion_event'] = modelhub.map.is_conversion_event(df, 'github_press')
    conversions = modelhub.aggregate.unique_users(df[df.is_conversion_event])

We use the earlier created `daily_users` to calculate the daily conversion rate.

.. code-block:: python

    conversion_rate = conversions / daily_users

From where do users convert most?

.. code-block:: python

    conversion_locations = modelhub.agg.unique_users(df[df.is_conversion_event],
                                                     groupby=['application', 'feature_nice_name', 'event_type'])


We can calculate what users did _before_ converting by combining several models from the model hub.

.. code-block:: python

    # label sessions with a conversion
    df['converted_users'] = modelhub.map.conversions_counter(df, name='github_press')>=1

    # label hits where at that point in time, there are 0 conversions in the session
    df['zero_conversions_at_moment'] = modelhub.map.conversions_in_time(df, 'github_press')==0

    # filter on above created labels
    converted_users = df[(df.converted_users & df.zero_conversions_at_moment)]

    # select only user interactions
    converted_users_filtered = converted_users[converted_users.stack_event_types>=['InteractiveEvent']]

    converted_users_features = modelhub.agg.unique_users(converted_users_filtered,
                                                         groupby=['application',
                                                                  'feature_nice_name',
                                                                  'event_type'])

At last we want to know how much time users that converted spent on our site before they converted. For this
we reuse the object we created above.

.. code-block:: python

    modelhub.aggregate.session_duration(converted_users, groupby=None).to_frame().head()
