.. _explore_data:

.. frontmatterposition:: 4

.. currentmodule:: bach_open_taxonomy

=================
Explore your data
=================

In this example, we briefly demonstrate how you can easily explore your new data collected with Objectiv.

This example is also available in a `notebook
<https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/explore-your-data.ipynb>`_
to run on your own data or use our `quickstart <https://objectiv.io/docs/home/quickstart-guide/>`_ to try it 
out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The data used in this example is based on the data set that comes with our quickstart docker demo.


A first look at the data
------------------------

.. code-block:: python

    # have a look at the data
    df.sort_values(['session_id', 'session_hit_number'], ascending=False).head()

Understanding the columns
-------------------------

.. code-block:: python

    # show the data type of each column
    df.dtypes

What is in these columns:

* `day`: the day of the session as a date.
* `moment`: the exact moment of the event.
* `user_id`: the unique identifier of the user based on the cookie.
* `global_contexts`: a json-like data column that stores additional information on the event that is logged. 
  This includes data like device data, application data, and cookie information. 
  :ref:`See this example notebook <open_taxonomy_location_stack_and_global_contexts>` for a more detailed 
  explanation.
* `location_stack`: a json-like data column that stores information on the exact location where the event is 
  triggered in the product's UI. 
  :ref:`See this example notebook <open_taxonomy_location_stack_and_global_contexts>` for more detailed 
  explanation.
* `event_type`: the type of event that is logged.
* `stack_event_types`: the parents of the event_type.
* `session_id`: a unique incremented integer id for each session. Starts at 1 for the selected data in the 
  DataFrame.
* `session_hit_number`: a incremented integer id for each hit in session ordered by moment.

Open Analytics Taxonomy
-----------------------
To get a good understanding of all the data and what you can get out of it, the open analytics taxonomy 
documentation is the place to go:

* `Event types, the stored data and hierarchy <https://objectiv.io/docs/taxonomy/events>`_.
* `Global contexts and what data you can find where <https://objectiv.io/docs/taxonomy/global-contexts>`_.
* `Location contexts to capture your product's UI in the data <https://objectiv.io/docs/taxonomy/location-contexts>`_.

Your first Objectiv event data
------------------------------
Before we dig any deeper, let's look at what data Objectiv is now tracking from your product. An easy way to 
do this, is by looking at it from the 'root locations', these are the main sections in your products UI.

Before we can do this, we first extract data from the Global Contexts and Location Stack. These columns 
contain all relevant context about the event. See more detailed examples on how you can do this in 
:ref:`this example notebook <open_taxonomy_location_stack_and_global_contexts>`.

.. code-block:: python

    # adding specific contexts to the data as columns
    df['application'] = df.global_contexts.gc.application
    df['root_location'] = df.location_stack.ls.get_from_context_with_type_series(type='RootLocationContext', key='id')
    df['path'] = df.global_contexts.gc.get_from_context_with_type_series(type='PathContext', key='id')

.. code-block:: python

    # now, we can easily slice the data using these columns
    event_data = modelhub.agg.unique_users(df, groupby=['application', 'root_location', 'path', 'event_type'])
    event_data.sort_values(ascending=False).to_frame().head(50)

Understanding product features
------------------------------
Objectiv captures the UI of your product in the data using the Location Context. This means, you can easily 
slice the data on any part of the UI that you're interested in. See 
:ref:`this example notebook <open_taxonomy_location_stack_and_global_contexts>`. It also means you can make 
product features very readable and easy to understand for your internal data reports.

.. code-block:: python

    # adding the readable product feature name to the data frame as column
    df['feature_nice_name'] = df.location_stack.ls.nice_name

.. code-block:: python

    # now, we can easily look at the data by product feature
    product_feature_data = modelhub.agg.unique_users(df, groupby=['feature_nice_name', 'event_type'])
    product_feature_data.sort_values(ascending=False).to_frame().head(50)

Get the SQL for any analysis
----------------------------

.. code-block:: python

    # just one analysis as an example, this works for anything you do with Objectiv Bach
    display_sql_as_markdown(product_feature_data)

Where to go next
----------------

Now that you had a first look at your new data collected with Objectiv, the best place to go next is looking 
at the :doc:`basic product analytics example notebook <./product-analytics>`. This will help you get familiar 
with product analytics metrics from Objectiv, straight from your raw data & ready to go.