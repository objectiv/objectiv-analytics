.. _bach_reference_series:

.. currentmodule:: bach

======
Series
======

.. autoclass:: Series
    :noindex:

Reference by function
---------------------

Creation / re-framing
~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    Series.to_frame
    Series.copy

Value accessors
~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    Series.head
    Series.to_pandas
    Series.array
    Series.value

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Axes
++++
.. autosummary::
    :toctree:

    Series.name
    Series.index
    Series.group_by
    Series.order_by

Types
+++++
.. autosummary::
    :toctree:

    Series.dtype
    Series.astype

Sql Model
+++++++++
.. autosummary::
    :toctree:

    Series.base_node
    Series.materialize
    Series.view_sql

Comparison and set operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    Series.all_values
    Series.any_value
    Series.exists
    Series.isin
    Series.isnull
    Series.notnull

Conversion, reshaping, sorting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    Series.reset_index
    Series.sort_index
    Series.sort_values
    Series.fillna
    Series.append
    Series.drop_duplicates
    Series.dropna
    Series.unstack

Function application, aggregation & windowing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    Series.agg
    Series.aggregate
    Series.apply_func

Computations & descriptive stats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All types
+++++++++

.. autosummary::
    :toctree:

    Series.describe
    Series.count
    Series.min
    Series.max
    Series.median
    Series.mode
    Series.nunique
    Series.value_counts


Window
++++++
.. autosummary::
    :toctree:

    Series.window_first_value
    Series.window_lag
    Series.window_nth_value
    Series.window_lead
    Series.window_last_value

    Series.window_row_number
    Series.window_rank
    Series.window_dense_rank
    Series.window_percent_rank

    Series.window_ntile
    Series.window_cume_dist
