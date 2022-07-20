.. _supported_data_stores:

.. frontmatterposition:: 5

.. currentmodule:: bach

=====================
Supported data stores
=====================
Our aim is to support all popular data stores with Bach. Currently we support `PostgreSQL 
</docs/tracking/collector/postgresql>`_ and `Google BigQuery </docs/tracking/collector/google-bigquery>`_; 
see below for more details and tips on each. Our roadmap includes Amazon Athena, Databrick, Redshift, 
Clickhouse, etcetera.

PostgreSQL
---------------
Out of the box, the Objectiv Collector `comes with a PostgreSQL database 
</docs/tracking/collector/postgresql>`_. There are no known compatibility issues - please let us know if you 
find any.

Google BigQuery
---------------
Google BigQuery is supported via a Snowplow pipeline. See `how to set up Google BigQuery 
</docs/tracking/collector/google-bigquery>`_.

A few things are useful to keep in mind while modeling on BigQuery, see the tips below.

**Use valid column names**

The Series in a Bach DataFrame map directly to database columns, hence a Series name must be a valid 
BigQuery column name, and contain only letters (`a-z`, `A-Z`), numbers (`0-9`), or underscores (`_`), and 
it must start with a letter or underscore. Consider this especially when using 
:py:meth:`DataFrame.unstack()`.

**Use a data sample**

Querying big datasets can be expensive with BigQuery. To get a smaller sample of the current DataFrame, 
use :py:meth:`DataFrame.get_sample()`:

.. code-block:: console

    table_name = 'objectiv-production.writable_dataset.table_name'
    df.get_sample(table_name, sample_percentage=10)

This creates a permanent table, so make sure you have a write access.

**Use temporary tables to limit query complexity**

Sometimes complex operations on Bach cannot be executed on BigQuery and you might get an error:

    Resources exceeded during query execution: Not enough resources for query planning - too many 
    subqueries or query is too complex.

If the underlying SQL query is complex for your dataset and you still need to apply other operations, in order 
to avoid the query becoming too complex (and getting the error above), you should first materialize the 
current DataFrame as a temporary table:

.. code-block:: console

    df = df.materialize(materialization='temp_table')

and then continue to do all the other operations. 

One way of checking SQL complexity is to print the resulting query:

.. code-block:: console

    display_sql_as_markdown(df)
