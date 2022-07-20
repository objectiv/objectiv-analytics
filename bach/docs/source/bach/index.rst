.. _bach:

.. currentmodule:: bach

.. frontmatterposition:: 3


====
Bach
====

Bach is Objectiv's data modeling library. With Bach, you can compose models with familiar Pandas-like
dataframe operations in your notebook. It uses an SQL abstraction layer that enables models to run on the
full dataset, and you can output models to SQL with a single command. It includes a set of operations that
enable effective feature creation for data sets that embrace the open analytics taxonomy.

If you want to use Bach, install the package from PyPI as follows:

.. code-block:: console

    pip install objectiv-bach
    pip install objectiv-bach[bigquery]  # when you want bigquery support

To get a taste of what you can do with Objectiv Bach, there's also a `demo </docs/home/quickstart-guide>`_ 
that enables you to run the full Objectiv pipeline on your local machine. It includes our website as a demo 
app, a Jupyter Notebook environment with working models and a Metabase environment to output data to.

.. toctree::
    :hidden:

    what-is-bach
    core-concepts
    examples
    api-reference/index




