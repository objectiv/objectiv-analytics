.. _models_reference_aggregation:

.. frontmatterposition:: 2

===========
Aggregation
===========

Aggregation models perform multiple Bach instructions that run some of the more common data analyses or
product analytics metrics. Always return aggregated data in some form from the
:class:`DataFrame <bach.DataFrame>` the model is applied to. Aggregation models can be accessed with the
:attr:`aggregate <modelhub.ModelHub.aggregate>` accessor from a model hub instance.

.. currentmodule:: modelhub

.. autoclass:: Aggregate

.. currentmodule:: modelhub.Aggregate

.. autosummary::
    :toctree: 
    :recursive:

    unique_users
    unique_sessions
    session_duration
    frequency
    retention_matrix
    top_product_features
    top_product_features_before_conversion



