.. currentmodule:: bach

.. frontmatterposition:: 3

=============
Core Concepts
=============
Bach aims to make life for the DS as simple and powerful as possible by using a very familiar interface. We
use two main concepts to achieve that, see below.

Delayed database operations
---------------------------
Regular operations on DataFrames and Series do not trigger any operations on the database, nor do they
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
We are striving for a pandas-compatible API, such that everyone that already knows pandas can get started
with Bach in mere minutes.

However, there are differences between Bach's API and pandas's API. Pandas is a big product, and it has a lot
of functionality that we have not yet implemented. Additionally we have some functions that pandas doesn't
have, and some of our functions have slightly different parameters.

Of course the fundamental difference is in how data is stored and processed: in local memory vs in the
database. This also results in a few differences in how DataFrames from both libraries work in certain
situations:

* The order of rows in a Bach DataFrame can be non-deterministic. If there is no deterministic
  :py:meth:`DataFrame.sort_values()` or :py:meth:`DataFrame.fillna()` call, then the order of the rows that 
  the data-transfer functions return can be unpredictable. In case for :py:meth:`DataFrame.fillna()`, 
  methods `ffill` and `bfill` might fill gaps with different values since rows containing `NULL`/`None` can 
  yield a different order of rows.
* Bach DataFrames can distinguish between `NULL`/`None` and Not-a-Number (`NaN`). Pandas generally doesn't
  and mainly uses NaN. When outputting data from a Bach DataFrame to a pandas DataFrame, most of this
  distinction is lost again.
* In a Bach DataFrame column names must be unique, in pandas this is not the case.