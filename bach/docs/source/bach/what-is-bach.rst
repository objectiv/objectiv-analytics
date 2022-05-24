.. _bach_whatisbach:

.. frontmatterposition:: 2

=============
What is Bach?
=============
Bach is a library for analysing data that is stored in a SQL database. Currently we only support Postgres,
but we plan on supporting more databases. We're using an interface that's mostly compatible with `pandas
<https://pandas.pydata.org/docs/reference/index.html>`_. All data storage and
processing is handled by the database. As a result, local memory does not limit the size of the data that
can be analysed with Bach.

The two main data classes of Bach are the DataFrame and Series:

* A :py:class:`DataFrame` represents data in a tabular form, with all rows having the same
  columns, and each column having a specific data type and a distinct name.
* A :py:class:`Series` object represents a single column in a DataFrame, with
  different subclasses per data type that allow for type specific operations.

Get started with Bach
---------------------
Once your app is set up with the Objectiv tracker and the collector is running, follow the steps in 
:ref:`Bach basics <bach_examples>` to work with the data in python using Objectiv.