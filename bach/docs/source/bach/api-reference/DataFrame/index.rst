.. _bach_reference_dataframe:

.. currentmodule:: bach

=========
DataFrame
=========

.. autoclass:: DataFrame
    :noindex:

Reference by function
---------------------

Creation
~~~~~~~~
.. autosummary::
    :toctree:

    DataFrame.from_table
    DataFrame.from_model
    DataFrame.from_pandas
    DataFrame.copy

Value accessors
~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    DataFrame.head
    DataFrame.to_pandas
    DataFrame.loc

Attributes and underlying data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Axes
++++
.. autosummary::
    :toctree:

    DataFrame.index
    DataFrame.data
    DataFrame.all_series
    DataFrame.index_columns
    DataFrame.data_columns
    DataFrame.group_by
    DataFrame.order_by

Types
+++++
.. autosummary::
    :toctree:

    DataFrame.dtypes
    DataFrame.index_dtypes
    DataFrame.astype

Sql Model
+++++++++
.. autosummary::
    :toctree:

    DataFrame.materialize
    DataFrame.get_sample
    DataFrame.get_unsampled
    DataFrame.view_sql

Variables
+++++++++
.. autosummary::
    :toctree:

    DataFrame.create_variable
    DataFrame.set_variable
    DataFrame.get_all_variable_usage


Reshaping, indexing, sorting & merging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    DataFrame.sort_index
    DataFrame.sort_values
    DataFrame.rename
    DataFrame.drop
    DataFrame.drop_duplicates
    DataFrame.dropna
    DataFrame.reset_index
    DataFrame.set_index
    DataFrame.merge
    DataFrame.append
    DataFrame.fillna
    DataFrame.ffill
    DataFrame.bfill
    DataFrame.stack
    DataFrame.unstack
    DataFrame.scale
    DataFrame.minmax_scale
    DataFrame.get_dummies

Aggregation & windowing
~~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::
    :toctree:

    DataFrame.agg
    DataFrame.aggregate
    DataFrame.groupby
    DataFrame.rollup
    DataFrame.cube
    DataFrame.window
    DataFrame.rolling
    DataFrame.expanding

.. _DataFrame.stats:

Computations & descriptive stats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All types
+++++++++
.. autosummary::
    :toctree:

    DataFrame.describe
    DataFrame.count
    DataFrame.min
    DataFrame.max
    DataFrame.median
    DataFrame.mode
    DataFrame.nunique
    DataFrame.value_counts

Numeric
+++++++
.. autosummary::
    :toctree:

    DataFrame.mean
    DataFrame.quantile
    DataFrame.sem
    DataFrame.sum
    DataFrame.std
    DataFrame.var

Visualization
++++++++++++++
.. autosummary::
    :toctree:

    DataFrame.plot