.. _models_reference_mapping:

.. frontmatterposition:: 1

================
Helper functions
================

Helper functions always return a series with the same shape and index as the
:class:`DataFrame <bach.DataFrame>` they are applied to. This ensures they can be added as a column to that
DataFrame. Helper functions that return :class:`SeriesBoolean <bach.SeriesBoolean>` can be used to filter
the data. The helper functions can be accessed with the :attr:`map <modelhub.ModelHub.map>` accessor from a 
model hub instance.

.. currentmodule:: modelhub

.. autoclass:: Map

.. currentmodule:: modelhub.Map

.. autosummary::
    :toctree: 
    :recursive:

    is_first_session
    is_new_user
    is_conversion_event
    conversions_counter
    conversions_in_time
    pre_conversion_hit_number
    retention_matrix



