.. _example_modelhub_basics:

.. frontmatterposition:: 5

.. currentmodule:: bach

=====================
Open model hub basics
=====================

In this example, we briefly demonstrate how you can use pre-built models from the open model hub in
conjunction with, :ref:`Bach <bach>`, our modeling library.

This example uses real, unaltered data that was collected from https://objectiv.io with Objectiv’s Tracker. All models
in the open model hub are compatible with data sets that have been validated against the
`open analytics taxonomy
<https://objectiv.io/docs/taxonomy/>`_.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/model-hub-demo-notebook.ipynb>`_
to run on your own data or use our
`quickstart
<https://objectiv.io/docs/home/quickstart-guide/>`_ to try it out with demo data in 5 minutes.

At first we have to install the open model hub and instantiate the Objectiv DataFrame object. See
:ref:`getting_started_with_objectiv` for more info on this.

Using the open model hub
------------------------
The open model hub is a growing collection of open-source, free to use data models that you can take,
combine and run for product analysis and exploration. It includes models for a wide range of typical product
analytics use cases. The source is available for all models and you're free to make any changes to them.

The model hub has two main type of functions: :ref:`models_reference_mapping` and 
:ref:`models_reference_aggregation`.

- `map` functions always return a series with the same shape and index as the DataFrame they are applied to.
  This ensures they can be added as a column to that DataFrame. `map` functions that return SeriesBoolean can
  be used with to filter the data.
- `aggregate` fuctions return aggregated data in some form from the DataFrame. Can also be accessed with
  `agg`.

Most of the model hub models take `data` as their first argument: this is the DataFrame with the Objectiv data to apply the model to.

The next examples demonstrate how to use the model hub by showcasing a selection of the models from the model hub.

A simple aggregation model
--------------------------
Calculating the unique users is one of the basic models in the model hub. As it is an aggregation model, it is called with `model_hub.aggregate.unique_users()`. It uses the *time_aggregation* that is set when the model hub was instantiated. With `.head()` we immediately query the data to show the results. `.to_pandas()` can be used to use all results as a pandas object in python.

.. code-block:: python

    modelhub.aggregate.unique_users(df)

Using `map` with the model hub & combining models
-------------------------------------------------
This example shows how you use map to label users as a new user. This uses *time_aggregation*. As *time_aggregation* was set to 'YYYY-MM-DD' it means all hits are labeled as new for the entire day in which the user had its first session.

.. code-block:: python

    df['is_new_user'] = modelhub.map.is_new_user(df)

Or we can label conversion events. To do this we first have to define what a conversion is by setting the
type of event and the location on the product at which this event was triggered with `add_conversion_event`
(this is called the location stack, see :ref:`location_stack` for info).

.. code-block:: python

    modelhub.add_conversion_event(location_stack=df.location_stack.json[{'id': 'Quickstart Guide', '_type': 'LinkContext'}:],
                                  event_type='PressEvent',
                                  name='quickstart_presses')
    df['conversion_events'] = modelhub.map.is_conversion_event(df, 'quickstart_presses')

Map, filter, aggregate
----------------------
As the map functions above retured a SeriesBoolean, they can be used in the model hub combined with a filter and aggregation models. We use the same aggregation model we showed earlier (`unique_users`), but now with the filter `df.conversion_events` applied. This gives the unique converted users per day.

.. code-block:: python

    modelhub.aggregate.unique_users(df[df.conversion_events]).head(10)

Similarly, we can use other aggregation models from the model hub. In the example below, the average session duration is calculated for new users.

.. code-block:: python

    modelhub.aggregate.session_duration(df[df.is_new_user])

Combining model results
-----------------------
Results from aggregation models can be used together if they share the same index type (similar to pandas). In this example the share of new users per day is calculated.

.. code-block:: python

    modelhub.agg.unique_users(df[df.is_new_user]) / modelhub.agg.unique_users(df)

Using multiple model hub filters
--------------------------------
The model hub's map results can be combined and reused. In this example we set two `map` model results as a column to the original DataFrame and use them both to filter the data and apply an aggregation model.
In this example we calculate the number of users that were new in a month and also that converted twice on a day.

.. code-block:: python

    df['is_new_user_month'] = modelhub.map.is_new_user(df, time_aggregation = 'YYYY-MM')
    df['is_twice_converted'] = modelhub.map.conversions_in_time(df, name='quickstart_presses')==2
    modelhub.aggregate.unique_users(df[df.is_new_user_month & df.is_twice_converted]).head()


What's next?
------------
There are several options on how to continue working with the data or using the results otherwise, i.e. for visualization.

1. Export models to SQL
~~~~~~~~~~~~~~~~~~~~~~~
As mentioned, all operations and models performed on the DataFrame are run on the SQL data base. Therefore it is possible to view all objects as an SQL statement. For the `new_user_share` results that was created this looks as follows:

.. code-block:: python

    display_sql_as_markdown(new_user_share)

2. Export to metabase
~~~~~~~~~~~~~~~~~~~~~
Aggregation model results can be exported to Metabase, to visualize and share your results. This is done for the unique new users:

.. code-block:: python

    modelhub.to_metabase(modelhub.agg.unique_users(df[df.is_new_user]),
                         config={'name': 'Unique New Users'})

3. Further data crunching using the Bach Modeling Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All results from the model hub are in the form of Bach DataFrames or Series. This makes the model hub and Bach work seamlessly together.

.. code-block:: python

    # label the number of time a user is converted in a session at a moment using the model hub.
    df['conversion_count'] = modelhub.map.conversions_in_time(df, name='quickstart_presses')

    # use Bach to do any supported operation using pandas syntax.
    # select users that converted
    converted_users = df[df.conversion_events].user_id.unique()
    # select PressEvents of users that converted
    df_selection = df[(df.event_type == 'PressEvent') &
                      (df.user_id.isin(converted_users))]
    # calculate the number of PressEvents before conversion per session
    presses_per_session = df_selection[df_selection.conversion_count == 0].groupby('session_id').session_hit_number.count()

Show the results, now the underlying query is executed.

.. code-block:: python

    presses_per_session.head()

There is another :ref:`example <bach_examples>` that demonstrates what you can do with the Bach modeling
library, or head over to the :ref:`Bach API reference <bach_api_reference>` for a complete overview of the possibilities.

4. Export DataFrame and model hub results to pandas DataFrame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bach DataFrames and/or model hub results can always be exported to pandas. Since Bach DataFrame operation run on the full dataset in the SQL database, it is recommended to export to pandas if data small enough; ie by aggregation or selection.
By exporting the data to pandas you can use all the options from pandas as well as pandas compatible ML packages.

We plot the previously calculated presses per session before conversion using pandas built-in plotting methods.

.. code-block:: python

    # presses_per_session_pd is a pandas Series
    presses_per_session_pd = presses_per_session.to_pandas()
    presses_per_session_pd.hist()

This concludes the open model hub demo.

We hope you’ve gotten a taste of the power and flexibility of the open model hub to quickly answer common product analytics questions. You can take it a lot further and build highly specific model stacks for in-depth analysis and exploration.

For a complete overview of all available and upcoming models, check out the :ref:`models <models>`.