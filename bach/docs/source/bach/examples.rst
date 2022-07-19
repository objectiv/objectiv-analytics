.. _bach_examples:

.. currentmodule:: bach

.. frontmatterposition:: 4

========
Examples
========
Here we'll give some very basic examples of the usage of Bach: creating a DataFrame, basic operations,
aggregate operations, and getting the resulting data filtered and sorted. For this example there is no
separate notebook available, but the operations demonstrated here are used in the other example notebooks.

In the examples we'll assume that the database has a table called 'example', with a few specific
columns. The SQL to create that table can be found below in :ref:`appendix_example_data`.

To get a taste of what you can do with Objectiv Bach, There is a `demo
</docs/home/quickstart-guide>`_ available that enables you to run the full Objectiv pipeline
on your local machine. It includes our website as a demo app, a Jupyter Notebook environment with working
models and a Metabase environment to output data to.


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

It is also possible to create a DataFrame from an arbitrary sql query (using 
:py:meth:`from_model <DataFrame.from_model>`) or from an existing pandas DataFrame (using 
:py:meth:`from_pandas <DataFrame.from_pandas>`).

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
    df = df.drop(columns=['city'])
    # rename the 'another column' column to 'city'
    df = df.rename(columns={'another column': 'city'})

    # Convert the Bach DataFrame to a pandas DataFrame.
    # When executing in a notebook this will print the dataframe.
    df.to_pandas()

The above operations add/remove/rename some columns of the DataFrame. However no actual query is executed
on the Database, until :py:meth:`df.to_pandas() <DataFrame.to_pandas>` is called. The DataFrame operations 
merely change the symbolic representation of the data in the DataFrame and its Series.

The call to :py:meth:`df.to_pandas() <DataFrame.to_pandas>` here is merely for demonstration purposes, in 
situations with bigger data sets it should be avoided until the data is needed as it will query the database 
and transfer all data.


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

The above example demonstrates how we can calculate aggregate functions (in this case 
:py:meth:`max() <DataFrame.max>`) on a group of row within a window that contains rows. Additionally it shows 
how to merge two DataFrames. Again only the optional debug statement 
:py:meth:`df.to_pandas() <DataFrame.to_pandas>` runs a query, the other operations merely update the internal 
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


The above example demonstrates filtering out rows and sorting a DataFrame. Without the 
:py:meth:`sort_values() <DataFrame.sort_values>` the order of the returned rows is non-deterministic. 
:py:meth:`view_sql() <DataFrame.view_sql>` can be used to show the compiled SQL query that
encompasses all operations done so far.


Filtering by Index Labels
------------------------------
.. important::
    In the following examples we call the :py:meth:`to_pandas() <DataFrame.to_pandas>` method multiple times, 
    but we do it only for visualization purposes. Please use :py:meth:`to_pandas() <DataFrame.to_pandas>` 
    only when necessary, as this will execute the frame's current query.

Here we construct a simple dataframe for illustrating the label selection functionality:

.. ipython:: python

    import pandas
    data = {
        'skating_order': [1, 2, 3, 4, 5],
        'city': ['Ljouwert', 'Snits', 'Drylts', 'Sleat', 'Starum'],
        'municipality': ['Leeuwarden', 'Súdwest-Fryslân', 'Súdwest-Fryslân', 'De Friese Meren', 'Súdwest-Fryslân'],
        'inhabitants': [1285, 1456, 1268, 1426, 1061],
    }
    pdf = pandas.DataFrame(data)

    df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
    df = df.set_index('city')
    df.to_pandas()


If you want to select a specific row from the frame, you can simply pass the label to the 
:py:meth:`loc() <DataFrame.loc>` property:

.. ipython:: python

    df.loc['Drylts'].to_pandas()

You can observe that the previous result returned a **Bach Series**, this will always be the return-type for
**Single-Label Selection**, where all selected columns are stacked into one single index series.

If you require just a subset of the columns, you can pass them as a second parameter:

.. ipython:: python

    df.loc['Drylts', ['inhabitants', 'skating_order']].to_pandas()

This will still return a series, the main difference is that only ``inhabitants`` and ``skating_order`` are
considered in the stacked index.

.. note::
    If a column included in the selection does not exist in the frame, this will raise an error.


In case you want to select/filter rows based on multiple labels, you can pass a list of labels:

.. ipython:: python

    df.loc[['Drylts', 'Ljouwert'], 'municipality'].to_pandas()

The code from above will return a **Bach DataFrame** instead, this will always be the return-type for
**List-Label Selection**.

**Slicing-Selection by labels** is also possible, for both rows and columns. Note the next example:

.. warning::
    Before slicing a frame's rows, you must sort it first. As slicing is a non-deterministic operation.

.. ipython:: python

    df.sort_index().loc['Sleat':, 'municipality':].to_pandas()

In case you need to select a value based on a condition, a series boolean can also be passed to the 
:py:meth:`loc() <DataFrame.loc>` property.

.. ipython:: python

  df.loc[df['inhabitants'] > 1300].to_pandas()

In previous examples, we selected rows by labels that actually exist in the frame. In case a label doesn't exist
in the frame, this will not raise any error since Bach has no notion of which values exist in the frame.

.. ipython:: python

    df.loc['x'].to_pandas()

Setting Values to DataFrame Subset
----------------------------------

In previous section we played around a bit with the :py:meth:`loc() <DataFrame.loc>` property, by just 
filtering the frame using labels. As in pandas, you are also able to set values to a specific group of rows 
and update the main frame. This works for all types of selections.

.. ipython:: python

    df.loc['Drylts'] = 'x'
    df.to_pandas()

You can see that the previous code block, sets all series to 'x' where the index is equal to `Drylts`.

.. note::

    If the value being set has a different ``dtype`` than the series to be modified, the series's ``dtype``
    will be changed to **string**. This does not apply if both have a numerical ``dtype``.

.. ipython:: python

    df = df.sort_index()
    df.loc['Sleat':, 'municipality'] = 'Fryslân'
    df.to_pandas()

As we mentioned, setting a value is possible for any type of selection. Notice that sorting is also needed for
this case.

.. important::
    ``df.sort_index().loc['Sleat':, 'municipality'] = 'Fryslân'`` will have no effect on ``df``, since
    :py:meth:`sort_index() <DataFrame.sort_index>` returns a new DataFrame.

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
