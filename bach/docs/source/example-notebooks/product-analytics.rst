.. _example_product_analytics:

.. frontmatterposition:: 2

.. currentmodule:: bach_open_taxonomy

=======================
Basic product analytics
=======================

This example shows how the open model hub can be used for basic product analytics. It's also available in a 
`notebook <https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/basic-product-analytics.ipynb>`_
to run on your own data, or use our `quickstart <https://objectiv.io/docs/home/quickstart-guide/>`_ to try it 
out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The data used in this example is based on the data set that comes with our quickstart docker demo. Let's have 
a look:

.. code-block:: python

    df.sort_values('session_id', ascending=False).head()

The columns 'global_contexts' and the 'location_stack' contain most of the event specific data. These columns
are json type columns and we can extract data from it based on the keys of the json objects using
:doc:`get_from_context_with_type_series <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.objectiv>`.
Or use methods specific to the :ref:`location_stack` or :ref:`global_contexts` to extract the data.


.. code-block:: python

    # add 'application', 'feature_nice_name' and 'root_location' as columns, so that we can use it for grouping etc later
    df['application'] = df.global_contexts.gc.application
    df['feature_nice_name'] = df.location_stack.ls.nice_name
    df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
    
    # have a look at the data
    df.sort_values(['session_id', 'session_hit_number'], ascending=False).head()

Now we will go though a selection of basic analytics metrics. We can use models from the :ref:`models
<models>`
for this purpose or use :ref:`Bach <bach>` to do data analysis directly on the data stored in the SQL database using
pandas-like syntax.

For each example, `head()`, `to_pandas()` or `to_numpy()` can be used to execute the generated SQL and get
the results in your notebook.

Unique users
------------
The `daily_users` uses the `time_aggregation` as set when the model hub was instantiated. In this case
`time_aggregation` was set to '%Y-%m-%d', so the aggregation is daily. For `monthly_users`, the
default time_aggregation is overridden by using a different `groupby`.

.. code-block:: python

    # model hub: unique users, monthly
    monthly_users = modelhub.aggregate.unique_users(df, groupby=modelhub.time_agg(df, '%Y-%m'))
    monthly_users.sort_index(ascending=False).head()

.. code-block:: python

    # model hub: unique users, daily
    daily_users = modelhub.aggregate.unique_users(df)
    daily_users.sort_index(ascending=False).head(10)

.. code-block:: python

    # model hub: unique users, per main product section
    users_root = modelhub.aggregate.unique_users(df, groupby=['application', 'root_location'])
    users_root.sort_index(ascending=False).head(10)

Retention
---------
To measure how well we are doing at keeping the users with us after the first interaction, we can use a retention matrix.

To calculate the retention matrix, we need to distribute the users into mutually exclusive cohorts based on the `time_period` (it can be `daily`, `weekly`, `monthly`, or `yearly`) when they first interacted.

In the retention matrix:
    - each row represents a cohort,
    - each column represents a time range, where time is calculated with respect to the cohort start time,
    - the values of the matrix elements are the number or percentage (depending on `percentage` parameter) of users in a given cohort that returned again in a given time range.

N.B. the users' activity starts to be traced from start_date specified in modelhub where we load the data: `modelhub.get_objectiv_dataframe(start_date='2022-02-02')`.

.. code-block:: python

    retention_matrix = modelhub.aggregate.retention_matrix(df, time_period='monthly', percentage=True, display=True)
    retention_matrix.head()

**Drilling down cohorts**

From our retention matrix, we can see that in the second cohort there is a drop in retained users in the next month, just 3.6% came back. We can try to zoom in on the different cohorts and see what is the difference.

.. code-block:: python

    # calculate the first cohort
    cohorts = df[['user_id', 'moment']].groupby('user_id')['moment'].min().reset_index()
    cohorts = cohorts.rename(columns={'moment': 'first_cohort'})

    # add first cohort of the users to our DataFrame
    df_with_cohorts = df.merge(cohorts, on='user_id')

    # filter data where users belong to # 0 cohort
    cohort0_filter = (df_with_cohorts['first_cohort'] > datetime(2022, 2, 1)) & (df_with_cohorts['first_cohort'] < datetime(2022, 3, 1))
    df_with_cohorts[cohort0_filter]['event_type'].value_counts().head()

    # filter data where users belong to # 1 cohort (the problematic one)
    cohort1_filter = (df_with_cohorts['first_cohort'] > datetime(2022, 3, 1)) & (df_with_cohorts['first_cohort'] < datetime(2022, 4, 1))
    df_with_cohorts[cohort1_filter]['event_type'].value_counts().head()

It is interesting to see that we have relatively more `VisibleEvent` in the first cohort than in second 'problematic' one.

This is  just a simple example to demonstrate the differences you can find between the cohorts, one can do similar tests e.g. with `top product features
<https://objectiv.io/docs/modeling/open-model-hub/models/aggregation/top_product_features/>`_, or develop more in-depth analysis depending on the product needs.

User time spent
---------------
We can also calculate the average session duration for time intervals. `duration_root_month` gives the
average time spent per root location per month.

.. code-block:: python

    duration_daily = modelhub.aggregate.session_duration(df)
    duration_monthly = modelhub.aggregate.session_duration(df, groupby=modelhub.time_agg(df, '%Y-%m'))
    duration_root_month = modelhub.aggregate.session_duration(df, groupby=['root_location', modelhub.time_agg(df, '%Y-%m')])

This example shows the quartiles of time spent. Materialization is needed because the expression of the
created series contains aggregated data, and it is not allowed to aggregate that.

.. code-block:: python

    session_duration = modelhub.aggregate.session_duration(df, groupby='session_id', exclude_bounces=False)
    session_duration.materialize().quantile(q=[0.25, 0.50, 0.75]).head()

Top used product features
-------------------------
Let's get the top used features in the product by our users, for that we can call the `top_product_features` function from the model hub.

.. code-block:: python

    top_product_features = modelhub.aggregate.top_product_features(df)
    top_product_features.head()

Top used product areas
----------------------

First we use the model hub to get the unique users per application, root location, feature, and event type.
From this prepared dataset, we show the users for the home page first.

.. code-block:: python

    # select only user actions, so stack_event_types must contain 'InteractiveEvent'
    interactive_events = df[df.stack_event_types.json.array_contains('InteractiveEvent')]


    top_interactions = modelhub.agg.unique_users(interactive_events, groupby=['application','root_location','feature_nice_name', 'event_type'])
    top_interactions = top_interactions.reset_index()

    home_users = top_interactions[(top_interactions.application == 'objectiv-website') &
                                  (top_interactions.root_location == 'home')]
    home_users.sort_values('unique_users', ascending=False).head()

From the same `top_interactions` object, we can select the top interactions for the 'docs' page.

.. code-block:: python

    docs_users = top_interactions[top_interactions.application == 'objectiv-docs']
    docs_users.sort_values('unique_users', ascending=False).head()

Acquisition
-----------

We create a copy of the original df, as to not clutter our original df with columns that are only required for acquisition analysis.

.. code-block:: python

    df_acquisition = df.copy()
    # extract referrer and marketing contexts from the global contexts
    df_acquisition['referrer'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='HttpContext', key='referrer')
    df_acquisition['utm_source'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='source')
    df_acquisition['utm_medium'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='medium')
    df_acquisition['utm_campaign'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='campaign')
    df_acquisition['utm_content'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='content')
    df_acquisition['utm_term'] = df_acquisition.global_contexts.gc.get_from_context_with_type_series(type='MarketingContext', key='term')

User origin
~~~~~~~~~~~

.. code-block:: python

    # users by referrer
    modelhub.agg.unique_users(df_acquisition, groupby='referrer').sort_values(ascending=False).head()

Marketing
~~~~~~~~~
Calculate the number of users per campaign.

.. code-block:: python

    # users by marketing campaign
    campaign_users = modelhub.agg.unique_users(df_acquisition, groupby=['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'])
    campaign_users = campaign_users.reset_index().dropna(axis=0, how='any', subset='utm_source')

    campaign_users.sort_values('utm_source', ascending=True).head()

Look at top used features by campaign for only user interactions.

.. code-block:: python

    # users by feature per campaign source & term
    users_feature_campaign = modelhub.agg.unique_users(df_acquisition[
        df_acquisition.stack_event_types.json.array_contains('InteractiveEvent')],
                                                       groupby=['utm_source',
                                                                'utm_term',
                                                                'feature_nice_name',
                                                                'event_type'])
    users_feature_campaign = users_feature_campaign.reset_index().dropna(axis=0, how='any', subset='utm_source')

    users_feature_campaign.sort_values(['utm_source', 'utm_term', 'unique_users'], ascending=[True, True, False]).head()

Conversions
-----------
First we define a conversion event in the Objectiv DataFrame we created for acquisition analysis.

.. code-block:: python

    # create a column that extracts all location stacks that lead to our github
    df_acquisition['github_press'] = df_acquisition.location_stack.json[{'id': 'objectiv-on-github', '_type': 'LinkContext'}:]
    df_acquisition.loc[df_acquisition.location_stack.json[{'id': 'github', '_type': 'LinkContext'}:]!=[],'github_press'] = df_acquisition.location_stack

    # define which events to use as conversion events
    modelhub.add_conversion_event(location_stack=df_acquisition.github_press,
                                  event_type='PressEvent',
                                  name='github_press')

This can be used by several models from the model hub using the defined name ('github_press'). First we calculate
the number of unique converted users.

.. code-block:: python

    # model hub: calculate conversions
    df_acquisition['is_conversion_event'] = modelhub.map.is_conversion_event(df_acquisition, 'github_press')
    conversions = modelhub.aggregate.unique_users(df_acquisition[df_acquisition.is_conversion_event])
    conversions.to_frame().sort_index(ascending=False).head(10)

We use the earlier created `daily_users` to calculate the daily conversion rate.

.. code-block:: python

    # calculate conversion rate
    conversion_rate = conversions / daily_users
    conversion_rate.sort_index(ascending=False).head(10)

Conversions by marketing campaign.

.. code-block:: python

    # model hub: calculate conversions per marketing canpaign based on UTM data in MarketingContext
    campaign_conversions = modelhub.aggregate.unique_users(df_acquisition[df_acquisition.is_conversion_event],
                                                           groupby=['utm_source', 'utm_medium', 'utm_campaign'])
    campaign_conversions.reset_index().dropna(axis=0, how='any', subset='utm_source').head()

From which product feature do users convert most?

.. code-block:: python

    conversion_locations = modelhub.agg.unique_users(df_acquisition[df_acquisition.is_conversion_event],
                                                     groupby=['application', 'feature_nice_name', 'event_type'])

    # calling .to_frame() for nicer formatting
    conversion_locations.sort_values(ascending=False).to_frame().head()

We can calculate what users did _before_ converting.

.. code-block:: python

    top_features_before_conversion = modelhub.agg.top_product_features_before_conversion(df_acquisition, name='github_press')
    top_features_before_conversion.head()

At last we want to know how much time users that converted spent on our site before they converted.

.. code-block:: python

    # label sessions with a conversion
    df_acquisition['converted_users'] = modelhub.map.conversions_counter(df_acquisition, name='github_press') >= 1

    # label hits where at that point in time, there are 0 conversions in the session
    df_acquisition['zero_conversions_at_moment'] = modelhub.map.conversions_in_time(df_acquisition, 'github_press') == 0

    # filter on above created labels
    converted_users = df_acquisition[(df_acquisition.converted_users & df_acquisition.zero_conversions_at_moment)]

    modelhub.aggregate.session_duration(converted_users, groupby=None).to_frame().head()
