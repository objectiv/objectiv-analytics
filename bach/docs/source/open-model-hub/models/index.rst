.. _models:

.. currentmodule:: modelhub

.. frontmatterposition:: 3

======
Models
======

The open model hub is  toolkit that contains functions and models that can be applied on data collected
with Objectiv’s Tracker. There are three types of functions/models:
1. :doc:`Helper functions <helper-functions/index>`. These helper functions simplify manipulating and 
analyzing the data.
2. :doc:`Aggregation models <aggregation/index>`. These models consist of a combination of Bach
instructions that run some of the more common data analyses or product analytics metrics.
3. :doc:`Machine learning models <machine-learning/index>`.



Helper functions
----------------
Helper functions always return a series with the same shape and index as the
:class:`DataFrame <bach.DataFrame>` they are applied to. This ensures they can be added as a column to that
DataFrame. Helper functions that return :class:`SeriesBoolean <bach.SeriesBoolean>` can be used to filter
the data. The helper functions can be accessed with the :attr:`map <modelhub.ModelHub.map>` accessor from a 
model hub instance.


.. currentmodule:: modelhub.Map

.. autosummary::
    :toctree: helper-functions

    is_first_session
    is_new_user
    is_conversion_event
    conversions_counter
    conversions_in_time
    pre_conversion_hit_number


.. toctree::
    :hidden:

    helper-functions/index


.. currentmodule:: modelhub.Aggregate

Aggregation models
------------------
Aggregation models perform multiple Bach instructions that run some of the more common data analyses or
product analytics metrics. Always return aggregated data in some form from the
:class:`DataFrame <bach.DataFrame>` the model is applied to. Aggregation models can be accessed with the
:attr:`aggregate <modelhub.ModelHub.aggregate>` accessor from a model hub instance.

.. autosummary::
    :toctree: aggregation

    unique_users
    unique_sessions
    session_duration
    frequency
    retention_matrix
    top_product_features
    top_product_features_before_conversion


.. toctree::
    :hidden:

    aggregation/index


.. currentmodule:: modelhub

Machine learning models
-----------------------

Currently we support :class:`LogisticRegression <modelhub.LogisticRegression>` directly on Bach DataFrames 
and Series.

.. toctree::
    :hidden:

    machine-learning/index
