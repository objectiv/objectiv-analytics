.. currentmodule:: bach

========
Examples
========
Here we'll give some very basic examples of the usage of Bach: creating a DataFrame, basic operations,
aggregate operations, and getting the resulting data filtered and sorted.

In the examples we'll assume that the database has a table called 'example', with a few specific
columns. The SQL to create that table can be found below in :ref:`appendix_example_data`.

We also have `live example notebook <https://notebook.objectiv.io/lab?path=product_analytics.ipynb>`_ that
you can use to get a feel for Bach.


Create a DataFrame from a database table
----------------------------------------
.. code-block:: python

    from bach import from_table
    import sqlalchemy
    # Setup database connection
    engine = sqlalchemy.create_engine(DB_URL)
    # Create Bach DataFrame representing all the data in the 'example' table, with the 'city_id' as index
    df = from_table(engine, 'example', index=['city_id'])

The above fragment queries the database to get the table structure of the 'example' table. But it does not
query any of the data in 'example', and this thus works equally well for a tiny table as for a huge table.

It is also possible to create a DataFrame from an arbitrary sql query (using `from_model`) or from an
existing pandas DataFrame (using `from_pandas`).

Basic operations
----------------
.. code-block:: python

    # Adding a new column
    df['column_name'] = 1337
    # Setting a new column to the value of an existing column
    df['another column'] = df['city']
    # Add a column 'century' with the result of some arithmetic
    df['century'] = df['founding'] // 100 + 1
    # Add a column 'concat', with the result of concatenating strings
    df['concat'] = df['city'] + ' is located in ' + df['municipality']
    # remove the city column
    df.drop(columns=['city'], inplace=True)
    # rename the 'another column' column to 'city'
    df.rename(columns={'another column': 'city'}, inplace=True)

    # Convert the Bach DataFrame to a pandas DataFrame.
    # When executing in a notebook this will print the dataframe.
    df.to_pandas()

The above operations add/remove/rename some columns of the DataFrame. However no actual query is executed
on the Database, until `df.to_pandas()` is called. The DataFrame operations merely change the symbolic
representation of the data in the DataFrame and its Series.

The call to `df.to_pandas()` here is merely for demonstration purposes, in situations with bigger datasets it
should be avoided until the data is needed as it will query the database and transfer all data.


Aggregate operations
--------------------
.. code-block:: python

    # Group on century, select the 'inhabitants' column, and calculate the maximum value within the group
    df_max = df.groupby('century')[['inhabitants']].max()
    df_max = df_max.reset_index()
    # df_max has two columns: 'century' and 'inhabitants_max'
    # merge df_max back into df, the merge will be done on the 'century' column as that is in both df and df_max
    df = df.merge(df_max)

    # Alternative method: use a window function
    century_window = df.window('century')
    df['inhabitants_max_2'] = df['inhabitants'].max(century_window)

    # Convert the Bach DataFrame to a pandas DataFrame.
    # When executing in a notebook this will print the dataframe.
    df.to_pandas()

The above example demonstrates how we can calculate aggregate functions (in this case `max()`) on a group of
row within a window that contains rows. Additionally it shows how to merge two DataFrames. Again only
the optional debug statement `df.to_pandas()` runs a query, the other operations merely update the internal
state of the DataFrame and its Series.


Filtering, sorting, and output
------------------------------
.. code-block:: python

    # Only keep the rows for which inhabitants == inhabitants_max,
    # i.e. the cities that are the biggest of all cities founded in the same century
    df = df[df.inhabitants == df.inhabitants_max]
    # Sort by century
    df = df.sort_values('century')
    # Only keep selected columns
    df = df[['skating_order', 'municipality', 'inhabitants', 'founding', 'city']]

    # Query database.
    print(df.to_pandas())
    # Expected output:
    #          skating_order     municipality  inhabitants  founding        city
    # city_id
    # 5                    5  Súdwest-Fryslân          960      1061      Starum
    # 1                    1       Leeuwarden        93485      1285    Ljouwert
    # 10                  10        Waadhoeke        12760      1374  Frjentsjer
    # 2                    2  Súdwest-Fryslân        33520      1456       Snits

    # Show the SQL query used to generate the above output:
    print(df.view_sql())


The above example demonstrates filtering out rows and sorting a DataFrame. Without the `sort_values()` the
order of the returned rows is non-deterministic. `view_sql()` can be used to show the compiled SQL query that
encompasses all operations done so far.

.. _appendix_example_data:

Appendix: Example Data
----------------------
.. code-block:: sql

    CREATE TABLE example (
        city_id bigint,
        skating_order bigint,
        city text,
        municipality text,
        inhabitants bigint,
        founding bigint
    );
    insert into example(city_id, skating_order, city, municipality, inhabitants, founding) values
    (1,  1,  'Ljouwert',   'Leeuwarden',        93485, 1285),
    (2,  2,  'Snits',      'Súdwest-Fryslân',   33520, 1456),
    (3,  3,  'Drylts',     'Súdwest-Fryslân',   3055,  1268),
    (4,  4,  'Sleat',      'De Friese Meren',   700,   1426),
    (5,  5,  'Starum',     'Súdwest-Fryslân',   960,   1061),
    (6,  6,  'Hylpen',     'Súdwest-Fryslân',   870,   1225),
    (7,  7,  'Warkum',     'Súdwest-Fryslân',   4440,  1399),
    (8,  8,  'Boalsert',   'Súdwest-Fryslân',   10120, 1455),
    (9,  9,  'Harns',      'Harlingen',         14740, 1234),
    (10, 10, 'Frjentsjer', 'Waadhoeke',         12760, 1374),
    (11, 11, 'Dokkum',     'Noardeast-Fryslân', 12675, 1298);
