.. _example_notebooks:

.. frontmatterposition:: 4

=================
Example notebooks
=================


Here are several examples of how you can analyze and model data using the 
:ref:`open model hub <open_model_hub>`. All examples are also available as Jupyter notebooks from our `GitHub 
repository <https://github.com/objectiv/objectiv-analytics/tree/main/notebooks>`_ and can run if all 
`requirements <https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/requirements.txt>`_ are
installed.

To get started you will first have to instantiate the :ref:`open model hub <open_model_hub>` and create a 
Bach :class:`DataFrame <bach.DataFrame>` with Objectiv data. The :ref:`open model hub <open_model_hub>` uses 
this :class:`DataFrame <bach.DataFrame>` for its models. For a general introduction to 
Bach :class:`DataFrames <bach.DataFrame>`, see the :ref:`Bach <bach>` docs or some basic examples to get 
started :ref:`here <bach_examples>`.


.. _getting_started_with_objectiv:

Getting started with Objectiv
-----------------------------

Here we show how to install and instantiate the model hub.
The :ref:`open model hub <open_model_hub>` is installed with:

.. code-block:: console

    pip install objectiv-modelhub


Now we can import and instantiate the model hub and create a Bach :class:`DataFrame <bach.DataFrame>` with 
Objectiv data. This :class:`DataFrame <bach.DataFrame>` is used to analyze data collected with Objectiv's 
Tracker. The :class:`DataFrame <bach.DataFrame>` points to the data in the SQL database and all operations 
are done on this object. A start date and an end date can optionally be passed to limit the underlying data 
that is queried. The `time_aggregation` parameter determines the default formatting of the timestamp of 
events. This is useful for grouping to different time aggregations, i.e. monthly or daily.

In the example we assume that the data collected with Objectiv's tracker is stored in a table called
'example' in a database that can be accessed with `db_url`.

.. code-block:: python

    from modelhub import ModelHub
    # instantiate the model hub
    modelhub = ModelHub(time_aggregation='YYYY-MM-DD')
    # get the Bach DataFrame with Objectiv data
    df = modelhub.get_objectiv_dataframe(db_url='postgresql://objectiv:@localhost:5432/objectiv',
                                         start_date='2022-03-01',
                                         table_name='example')

Your :class:`DataFrame <bach.DataFrame>` is instantiated! We start with showing the first couple of rows 
from the data set.

.. code-block:: python

    df.head()

Take a look at one of the example notebooks below to see how you can analyze your data. Basic Bach
introduction examples are :ref:`here <bach_examples>`.

.. toctree::
    :maxdepth: 1

    machine-learning
    product-analytics
    user-intent
    feature-engineering
    modelhub-basics
    open-taxonomy
    feature_importance

