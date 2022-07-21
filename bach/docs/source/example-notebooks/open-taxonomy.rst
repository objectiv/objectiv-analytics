.. _example_open_taxonomy:

.. frontmatterposition:: 9

.. currentmodule:: bach

====================
Open taxonomy how-to
====================

This example demonstrates what you can do with the Objectiv Bach modeling library and a dataset that was 
validated against the `open analytics taxonomy <https://objectiv.io/docs/taxonomy/>`_. It's also available in 
a `notebook <https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/open-taxonomy-how-to.ipynb>`_
to run on your own data or use our `quickstart <https://objectiv.io/docs/home/quickstart-guide/>`_ to try it 
out with demo data in 5 minutes.

First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The data
--------
The index contains a unique identifier for every hit.

.. code-block:: python

    df.index_dtypes

The dtypes of columns can be displayed with:

.. code-block:: python

    df.dtypes

- `day`: the day of the session as a date.
- `moment`: the exact moment of the event.
- `user_id`: the unique identifier of the user based on the cookie.
- `global_contexts`: a json-like data column that stores additional information on the event that is logged. This includes data like device data, application data, and cookie information. See below for more detailed explanation.
- `location_stack`: a json-like data column that stores information on the exact location where the event is triggered in the product's UI. See below for more detailed explanation.
- `event_type`: the type of event that is logged.
- `stack_event_types`: the parents of the event_type.
- `session_id`: a unique incremented integer id for each session. Starts at 1 for the selected data in the DataFrame.
- `session_hit_number`: a incremented integer id for each hit in session ordered by moment.

Preview of the data. We show the latest PressEvents.

.. code-block:: python

    df[df.event_type == 'PressEvent'].sort_values('moment', ascending=False).head()

The Open Taxonomy
-----------------
Data in a DataFrame created with `get_objectiv_dataframe()` follows the principles of the `open analytics taxonomy
<https://objectiv.io/docs/taxonomy/>`_ and is stored as such. Therefore it adheres to the three principles of how events are structured.

- **event_type**: describes the kind of interactive or non-interactive event.
- **location_stack**: describes where an event originated from in the visual UI.
- **global_context**: general information to an event.

The following section will go through these concepts one by one.

event_type
~~~~~~~~~~
The event type describes what kind of event is triggered. The goal of the open taxonomy is to label all interactive and non-interactive events in a standardized way. Together with the location stack, the event_type 'defines' what happened with or on the product.

.. code-block:: python

    df[df.day == '2022-01-10'].event_type.head()

.. _open_taxonomy_location_stack_and_global_contexts:

location_stack & global_contexts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The location stack and global contexts are stored as json type data. Within the DataFrame, it is easy to access data in json data based on position or content.
**Slicing the json data**
With the `.json[]` syntax you can slice the array using integers. Instead of integers, dictionaries can also be passed to 'query' the json array. If the passed dictionary matches a context object in the stack, all objects of the stack starting (or ending, depending on the slice) at that object will be returned.

In case a json array does not contain the object, `None` is returned. More info at the :doc:`API reference <../bach/api-reference/Series/Json/index>`.

.. _location_stack:

location_stack
~~~~~~~~~~~~~~
The `location_stack` column in the DataFrame stores the information on the exact location where the event is triggered in the product. The example used above is the location stack of the link to the DataFrame API reference in the menu on our docs page.

Because of the specific way the location information is labeled, validated, and stored using the Open
Taxonomy, it can be used to slice and group your products' features in an efficient and easy way. The
column is set as an `objectiv_location_stack` type, and therefore location stack specific methods can be
used to access the data from the `location_stack`. These methods can be used using the `.ls` accessor on
the column. The methods are:

.. currentmodule:: modelhub.series.series_objectiv.SeriesLocationStack

* The property accessors:

  * :ref:`.ls.navigation_features <ls_navigation_features>`
  * :ref:`.ls.feature_stack <ls_feature_stack>`
  * :ref:`.ls.nice_name <ls_nice_name>` 

* All methods of :doc:`SeriesJson <../bach/api-reference/Series/Json/index>` for the json type can also be accessed using `.ls`

For example,

.. code-block:: python

    df.location_stack.ls.nice_name

returns '*Link: how-it-works located at Root Location: page-home => Content: main => Content: product-intro*' for the location stack mentioned above.

The full reference of location stack is `here <https://objectiv.io/docs/taxonomy/location-contexts>`_. An
example location stack for a PressEvent is queried below:

.. code-block:: python

    df[df.event_type == 'PressEvent'].location_stack.head(1)[0]


.. _global_contexts:

global_contexts
~~~~~~~~~~~~~~~
The `global_contexts` column in the DataFrame contain all information that is relevant to the logged event. As it is set as an `objectiv_global_context` type, specific methods can be used to access the data from the `global_contexts`. These methods can be used using the `.gc` accessor on the column. The methods are:

* :doc:`.gc.get_from_context_with_type_series(type, key) <../open-model-hub/api-reference/SeriesGlobalContexts/modelhub.SeriesGlobalContexts.objectiv>`.
* The property accessors:

  * :ref:`.gc.cookie_id <gc_cookie_id>`
  * :ref:`.gc.user_agent <gc_user_agent>`
  * :ref:`.gc.application <gc_application>`

* All methods of :doc:`SeriesJson <../bach/api-reference/Series/Json/index>` for the json type can also be accessed using `.gc`

The full `reference of global contexts is here
<https://objectiv.io/docs/taxonomy/global-contexts>`_. An
example is queried below:

.. code-block:: python

    df.global_contexts.head(1)[0]

Sampling
--------
One of the key features to Objectiv Bach is that it runs on your full data set. There can however be situations where you want to experiment with your data, meaning you have to query the full data set often. This can become slow and/or costly.

To limit these costs it is possible to do operations on a sample of the full data set. All operations can easily be applied at any time to the full data set if that is desired.

Below we create a sample that randomly selects ~1% of all the rows in the data. A table containing the sampled is written to the database, therefore the `table_name` must be provided when creating the sample.

.. code-block:: python

    # for BigQuery the table name should be 'YOUR_PROJECT.YOUR_WRITABLE_DATASET.YOUR_TABLE_NAME'
    df_sample = df.get_sample(table_name='sample_data', sample_percentage=10, overwrite=True)

Two new columns are created in the sample.

.. code-block:: python

    df_sample['root_location_contexts'] = df_sample.location_stack.json[:1]
    df_sample['application'] = df_sample.global_contexts.gc.application
    df_sample.sort_values('moment', ascending=False).head()

Using `.get_unsampled()`, the operations that are done on the sample (the creation of the two columns), are applied to the entire data set:

.. code-block:: python

    df_unsampled = df_sample.get_unsampled()
    df_unsampled.sort_values('moment', ascending=False).head()

The sample can also be used for grouping and aggregating. The example below counts all hits and the unique event_types in the sample:

.. code-block:: python

    df_sample_grouped = df_sample.groupby(['application']).agg({'event_type':'nunique','session_hit_number':'count'})
    df_sample_grouped.head()

As can be seen from the counts, unsampling applies the transformation to the entire data set:

.. code-block:: python

    df_unsampled_grouped = df_sample_grouped.get_unsampled()
    df_unsampled_grouped.head()

This concludes this demo.

We’ve demonstrated a handful of the operations that Bach supports and hope you’ve gotten a taste of what Bach can do for your modeling workflow.

The full Objectiv Bach API reference is available :doc:`here <../bach/api-reference/index>`.

There is another example that focuses on using the :doc:`open model hub <modelhub-basics>`, 
demonstrating how you can use the model hub and Bach to quickly answer common product analytics questions.