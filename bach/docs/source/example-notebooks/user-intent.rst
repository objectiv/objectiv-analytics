.. _example_user_intent:

.. frontmatterposition:: 3

.. currentmodule:: bach_open_taxonomy

==========================
Basic user intent analysis
==========================

This example shows how the open model hub can be used for basic user intent analysis. It's also available in 
a `notebook <https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/basic-user-intent.ipynb>`_
to run on your own data or use our `quickstart <https://objectiv.io/docs/home/quickstart-guide/>`_ to try it 
out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The data used in this example is based on the data set that comes with our quickstart docker demo.

Besides the open model hub, we have to import the following packages for this example:

.. code-block:: python

    from bach import display_sql_as_markdown
    import bach
    import pandas as pd
    from datetime import timedelta

The columns 'global_contexts' and the 'location_stack' contain most of the event specific data. These columns
are json type columns and we can extract data from it based on the keys of the json objects using
:doc:`get_from_context_with_type_series <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.objectiv>`. 
Or use methods specific to the :ref:`location_stack` or :ref:`global_contexts` to extract the data.

.. code-block:: python

    df['application'] = df.global_contexts.gc.application
    df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')

Exploring root location
-----------------------
The root_location context in the location_stack uniquely represents the top-level UI location of the user. As a first step of grasping user intent, this is a good starting point to see in what main areas of your product users are spending time.

.. code-block:: python

    # model hub: unique users per application and root location
    users_root = modelhub.aggregate.unique_users(df, groupby=['application', 'root_location'])
    users_root.sort_index().head(10)

Exploring session duration
--------------------------
The average `session_duration` model from the `open model hub </docs/modeling/open-model-hub/>`_ is another good pointer to explore first for user intent.

.. code-block:: python

    # model hub: duration, per application and root location
    duration_root = modelhub.aggregate.session_duration(df, groupby=['application', 'root_location']).sort_index()
    duration_root.head(10)

Now, we can look at the distribution of time spent. We used the Bach quantile operation for this. We'll use this distribution to define the different stages of user intent.

.. code-block:: python

    # how is this time spent distributed?
    session_duration = modelhub.aggregate.session_duration(df, groupby='session_id')
    # materialization is needed because the expression of the created series contains aggregated data, and it is not allowed to aggregate that.
    session_duration = session_duration.materialize()

    # show quantiles
    session_duration.quantile(q=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]).head(10)

Defining different stages of user intent
----------------------------------------
After exploring the `root_location` and `session_duration` (both per root location and quantiles), we can make a simple definition of different stages of user intent.

Based on the objectiv.io website data in the quickstart:

We think that users that spent most time (90th percentile) and specifically in our documentation sections are in the Implement phase of Objectiv. As there is a jump beyond the one minute mark at the 70th percentile, it feels sensible to deem that users beyond the 70th up to 90th perctile in our documentation sections are Exploring. The remaining users are Informing themselves about the product. Those users are spending less than 1:40 in the docs and/or spend any amount of time on our main website.

.. list-table::
   :widths: 20 50 30
   :header-rows: 1

   * - User intent
     - Root locations
     - Duration
   * - 1 - Inform
     - *all sections other than the ones mentioned below*
     - *any time spent*
   * - 1 - Inform
     - Docs: modeling, taxonomy, tracking, home
     - less than 1:40
   * - 2 - Explore
     - Docs: modeling, taxonomy, tracking, home
     - between 1:40 and 11:30
   * - 3 - Implement
     - Docs: modeling, taxonomy, tracking, home
     - more than 11:30

This is just for illustration purposes, you can adjust these definitions based on your own collected data.

Assigning user intent
---------------------
Based on the definitions above, we can start assigning a stage of intent to each user.

.. code-block:: python

    # set the root locations that we will use based on the definitions above
    roots = bach.DataFrame.from_pandas(engine=df.engine,
                                       df=pd.DataFrame({'roots': ['modeling', 'taxonomy', 'tracking', 'home', 'docs']}),
                                       convert_objects=True).roots

    # now we calculate the total time spent per _user_ and create a data frame from it
    user_intent_buckets = modelhub.agg.session_duration(df,
                                                        groupby=['user_id'],
                                                        method='sum',
                                                        exclude_bounces=False).to_frame()

    # same as above, but for selected roots only
    explore_inform_users_session_duration = modelhub.agg.session_duration((df[(df.root_location.isin(roots)) & (df.application=='objectiv-docs')]),
                                                                          groupby='user_id',
                                                                          method='sum')
    # and set it as column
    user_intent_buckets['explore_inform_duration'] = explore_inform_users_session_duration

    # first, we set the Inform bucket as a catch-all, meaning users that do not fall into Explore and Implement will be defined as Inform
    user_intent_buckets['bucket'] = '1 - inform'

    # calculate buckets duration
    user_intent_buckets.loc[(user_intent_buckets.explore_inform_duration >= timedelta(0, 100)) &
                            (user_intent_buckets.explore_inform_duration <= timedelta(0, 690)), 'bucket'] = '2 - explore'
    user_intent_buckets.loc[user_intent_buckets.explore_inform_duration > timedelta(0, 690), 'bucket'] = '3 - implement'

Now, we have assigned intent to each user and can for example look at the total number of users per intent bucket.

.. code-block:: python

    # total number of users per intent bucket
    user_intent_buckets.reset_index().groupby('bucket').agg({'user_id': 'nunique'}).head()

What's next?
------------
The are many next possible analysis steps, for example:

- What product features do each of the intent groups use?
- What kind of intent users come from different marketing campaigns?
- How can we drive more users to the 'Implement' stage? Look at different product features that users with the 'Implement' intent use, compared to 'Explore'.

A good starting point for these analyses on top of the user intent buckets is the basic product analytics example in the :doc:`example notebooks <index>`.


Get the SQL for this user intent analysis
-----------------------------------------

.. code-block:: python

    # get the SQL to use this analysis in for example your BI tooling
    display_sql_as_markdown(user_intent_buckets)