.. currentmodule:: bach

.. frontmatterposition:: 3

=============
Core Concepts
=============
Bach aims to make life for the DS as simple and powerful as possible by using a very familiar interface. We
use two main concepts to achieve that.

Delayed database operations
---------------------------
Regular operations on DataFrames and Series do not trigger any operations on the database nor do they
transfer any data from the database to Bach. All operations are combined and compiled to a single SQL query,
which is executed only when one of a few specific data-transfer functions is called on either a DataFrame or
a Series object:

* :py:meth:`DataFrame.to_pandas()` or :py:meth:`Series.to_pandas()`
* :py:meth:`DataFrame.head()` or :py:meth:`Series.head()`
* :py:meth:`DataFrame.to_numpy()` or :py:meth:`Series.to_numpy()`
* The property accessors :py:attr:`Series.array` and :py:attr:`Series.value`
* :py:meth:`DataFrame.unstack()` or :py:meth:`Series.unstack()`

Typical usage would be to do all heavy lifting inside the database, and only query the aggregated/summarized
output.

Additionally there are operations that write to the database:

* :py:meth:`DataFrame.database_create_table()`
* :py:meth:`DataFrame.from_pandas()`, when called with `materialization='table'`
* :py:meth:`DataFrame.get_sample()`

Compatibility with pandas
-------------------------
We are striving for a pandas compatible api, such that everyone that already knows pandas can get started
with Bach in mere minutes.

However there are differences between Bach's API and pandas's API. Pandas is a big product, and it has a lot
of functionality that we have not yet implemented. Additionally we have some functions that pandas doesn't
have, and some of our functions have slightly different parameters.

Of course the fundamental difference is in how data is stored and processed: in local memory vs in the
database. This also results in a few differences in how DataFrames from both libraries work in certain
situations:

* The order of rows in a Bach DataFrame can be non-deterministic. If there is not a deterministic
  :py:meth:`DataFrame.sort_values()` or :py:meth:`DataFrame.fillna()` call, then the order of the rows that the data-transfer
  functions return can be unpredictable. In case for :py:meth:`DataFrame.fillna()`, methods `ffill` and `bfill` might fill gaps
  with different values since rows containing `NULL`/`None` can yield a different order of rows.
* Bach DataFrames can distinguish between `NULL`/`None` and Not-a-Number (`NaN`). Pandas generally doesn't
  and mainly uses NaN. When outputting data from a Bach DataFrame to a pandas DataFrame, most of this
  distinction is lost again.
* In a Bach DataFrame column names must be unique, in pandas this is not the case


BigQuery Tips
-------------
The columns in Bach DataFrame are the database columns, hence the column name must contain only letters (`a-z`, `A-Z`), numbers (`0-9`), or underscores (`_`), and it must start with a letter or underscore. Especially remember this during [`DataFrame.unstack()`](/modeling/bach/api-reference/DataFrame/bach.DataFrame.unstack.mdx) usage.

For getting a sample of the data one can use:

.. code-block:: console

    table_name = 'objectiv-production.writable_dataset.table_name'
    df.get_sample(table_name, sample_percentage=10, overwrite=True)

It creates a permanent table, and if the table exists it overwrites it (make sure you have a write access). For BigQuery `seed` parameter is not implemented.

If you are planning to do a lot of operations on a given Bach DataFrame and already the underlying SQL query is complex it would be more optimal for the database first to materialize the current DataFrame as a temporary table:

.. code-block:: console

    df = df.materialize(materialization='temp_table')

and then continue to do all the other complex operations. One way of checking SQL complexity:

.. code-block:: console

    display_sql_as_markdown(df)
