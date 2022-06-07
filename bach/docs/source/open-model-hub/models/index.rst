.. _models:

.. currentmodule:: modelhub

.. frontmatterposition:: 2

======
Models
======

The open model hub is  toolkit that contains functions and models that can be applied on data collected
with Objectiv’s Tracker. There are three types of functions/models:
1. :ref:`Map <models_reference_mapping>` functions. These helper functions simplify manipulating and analyzing
the data tracked by Objectiv's tracker.
2. :ref:`Aggregate <models_reference_aggregation>` models. These models consist of a combination of Bach
instructions that run some of the more common data analyses or product analytics metrics.
3. Machine learning models that can be used with Bach data.



Map
---
Map functions always return a series with the same shape and index as the
:class:`DataFrame <bach.DataFrame>` they are applied to. This ensures they can be added as a column to that DataFrame. Map
functions that return :class:`SeriesBoolean <bach.SeriesBoolean>` can be used to filter the data.

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
---------
Aggregate models perform multiple Bach instructions that run some of the more common data analyses or
product analytics metrics. Always return aggregated data in some form from the
:class:`DataFrame <bach.DataFrame>` the model is applied to.

.. autosummary::
    :toctree: Aggregate

    unique_users
    unique_sessions
    session_duration
    frequency
    top_product_features
    top_product_features_before_conversion


.. toctree::
    :hidden:

    Aggregate/index

Machine Learning
----------------

Currently we support  :ref:`logistic regression <modelhub_reference_logistic_regression>` directly on Bach DataFrames and Series.
