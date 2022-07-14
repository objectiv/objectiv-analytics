.. _bach:

.. currentmodule:: bach

.. frontmatterposition:: 4


====
Bach
====

Bach is Objectiv's data modeling library to build & compose models with familiar `pandas
<https://pandas.pydata.org/docs/reference/index.html>`_-like dataframe operations in your notebook. It uses 
an SQL abstraction layer that enables models to run on the full dataset. As all data storage and processing 
is handled by the database, local memory does not limit the size of the data that can be analyzed. See more 
details on this in the :doc:`Core Concepts <./core-concepts>`. Any model you build can subsequently be output 
to SQL with a single command, for use in tools like BI or dbt. 

Bach also specifically includes a set of operations to work with datasets that embrace the 
`open analytics taxonomy </docs/taxonomy/>`_. 

The package can be installed from PyPI:

.. code-block:: console

    pip install objectiv-bach


How to use
----------
Once your app is `tracking data </docs/tracking/>`_, follow the steps in the :ref:`examples <bach_examples>` 
to work with Bach.

The two main data classes in Bach are the DataFrame and Series:

* A :py:class:`DataFrame` represents data in a tabular form, with all rows having the same columns, and each 
  column having a specific data type and a distinct name.
* A :py:class:`Series` object represents a single column in a DataFrame, with different subclasses per data 
  type that allow for type specific operations.


.. toctree::
    :hidden:

    core-concepts
    examples
    data-stores
    api-reference/index




