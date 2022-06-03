.. _models:

.. currentmodule:: modelhub

.. frontmatterposition:: 2

======
Models
======

The :ref:`open model hub <open_model_hub>` has two main types of models:
1. A collection of helper functions that perform multiple Bach instructions to make data analysis and
product analytics on data collected with Objectiv’s Tracker as easy as possible.
2. Machine learning models that can be used with Bach data.

Helper functions
----------------
There are two main type of helper functions:
:ref:`map <models_reference_mapping>` and :ref:`aggregate <models_reference_aggregation>`.

- :ref:`map <models_reference_mapping>` functions always return a series with the same shape and index as the 
  :class:`DataFrame <bach.DataFrame>` they are applied to. This ensures they can be added as a column to that 
  :class:`DataFrame <bach.DataFrame>`. :ref:`map <models_reference_mapping>` functions that return 
  :class:`DataFrame <bach.SeriesBoolean>` can be used with to filter the data.
- :ref:`aggregate <models_reference_aggregation>` functions return aggregated data in some form from the 
  :class:`DataFrame <bach.DataFrame>`. Can also be accessed with :meth:`agg <ModelHub.agg>`.


Map
~~~

.. currentmodule:: modelhub.Map

.. autosummary::
    :toctree: Map

    is_first_session
    is_new_user
    is_conversion_event
    conversions_counter
    conversions_in_time
    pre_conversion_hit_number


.. toctree::
    :hidden:

    Map/index


.. currentmodule:: modelhub.Aggregate

Aggregate
~~~~~~~~~

.. autosummary::
    :toctree: Aggregate

    unique_users
    unique_sessions
    session_duration
    frequency


.. toctree::
    :hidden:

    Aggregate/index

Machine Learning
----------------

Currently we support  :ref:`logistic regression <modelhub_reference_logistic_regression>` directly on Bach DataFrames and Series.