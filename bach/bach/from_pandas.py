"""
Copyright 2021 Objectiv B.V.
"""
from typing import Tuple, Dict

import pandas
from sqlalchemy.engine import Engine

from bach import DataFrame, get_series_type_from_dtype
from bach.types import value_to_dtype
from bach.expression import Expression, join_expressions
from sql_models.model import CustomSqlModelBuilder
from sql_models.util import quote_identifier


def from_pandas(engine: Engine,
                df: pandas.DataFrame,
                convert_objects: bool,
                name: str,
                materialization: str,
                if_exists: str = 'fail') -> DataFrame:
    """
    See DataFrame.from_pandas() for docstring.
    """
    if materialization == 'cte':
        return from_pandas_ephemeral(engine=engine, df=df, convert_objects=convert_objects, name=name)
    if materialization == 'table':
        return from_pandas_store_table(
            engine=engine,
            df=df,
            convert_objects=convert_objects,
            table_name=name,
            if_exists=if_exists
        )
    raise ValueError(f'Materialization should either be "cte" or "table", value: {materialization}')


def from_pandas_store_table(engine: Engine,
                            df: pandas.DataFrame,
                            convert_objects: bool,
                            table_name: str,
                            if_exists: str = 'fail') -> DataFrame:
    """
    Instantiate a new DataFrame based on the content of a Pandas DataFrame. This will first write the
    data to a database table using pandas' df.to_sql() method.
    Supported dtypes are 'int64', 'float64', 'string', 'datetime64[ns]', 'bool'


    :param engine: db connection
    :param df: Pandas DataFrame to instantiate as DataFrame
    :param convert_objects: If True, columns of type 'object' are converted to 'string' using the
        pd.convert_dtypes() method where possible.
    :param table_name: name of the sql table the Pandas DataFrame will be written to
    :param if_exists: {'fail', 'replace', 'append'}, default 'fail'
        How to behave if the table already exists:
        * fail: Raise a ValueError.
        * replace: Drop the table before inserting new values.
        * append: Insert new values to the existing table.
    """
    # todo add dtypes argument that explicitly let's you set the supported dtypes for pandas columns
    df_copy, index_dtypes, all_dtypes = _from_pd_shared(df, convert_objects, cte=False)

    conn = engine.connect()
    df_copy.to_sql(name=table_name, con=conn, if_exists=if_exists, index=False)
    conn.close()

    index = list(index_dtypes.keys())
    return DataFrame.from_table(engine=engine, table_name=table_name, index=index, all_dtypes=all_dtypes)


def from_pandas_ephemeral(
        engine: Engine,
        df: pandas.DataFrame,
        convert_objects: bool,
        name: str
) -> DataFrame:
    """
    Instantiate a new DataFrame based on the content of a Pandas DataFrame. The data will be represented
    using a `select * from values()` query.

    Warning: This method is only suited for small quantities of data.
    For anything over a dozen kilobytes of data it is recommended to store the data in a table in
    the database, e.g. by using the from_pd_store_table() function.

    Supported dtypes are 'int64', 'float64', 'string', 'datetime64[ns]', 'bool'

    :param engine: db connection
    :param df: Pandas DataFrame to instantiate as DataFrame
    :param convert_objects: If True, columns of type 'object' are converted to 'string' using the
        pd.convert_dtypes() method where possible.
    """
    # todo add dtypes argument that explicitly let's you set the supported dtypes for pandas columns
    df_copy, index_dtypes, all_dtypes = _from_pd_shared(df, convert_objects, cte=True)

    column_series_type = [get_series_type_from_dtype(dtype) for dtype in all_dtypes.values()]

    per_row_expr = []
    for row in df_copy.itertuples():
        per_column_expr = []
        # Access the columns in `row` by index rather than by name. Because if a name starts with an
        # underscore (e.g. _index_skating_order) it will not be available as attribute.
        # so we use `row[i]` instead of getattr(row, column_name).
        # start=1 is to account for the automatic index that pandas adds
        for i, series_type in enumerate(column_series_type, start=1):
            val = row[i]
            per_column_expr.append(series_type.value_to_expression(dialect=engine.dialect, value=val))
        row_expr = Expression.construct('({})', join_expressions(per_column_expr))
        per_row_expr.append(row_expr)
    all_values_str = join_expressions(per_row_expr, join_str=',\n').to_sql(engine.dialect)

    column_names_expr = join_expressions(
        [Expression.raw(quote_identifier(engine.dialect, column_name)) for column_name in all_dtypes.keys()]
    )
    column_names_str = column_names_expr.to_sql(engine.dialect)

    sql = f'select * from (values \n{all_values_str}\n) as t({column_names_str})\n'

    model_builder = CustomSqlModelBuilder(sql=sql, name=name)
    sql_model = model_builder()

    index = list(index_dtypes.keys())
    return DataFrame.from_model(engine=engine, model=sql_model, index=index, all_dtypes=all_dtypes)


def _from_pd_shared(
        df: pandas.DataFrame,
        convert_objects: bool,
        cte: bool
) -> Tuple[pandas.DataFrame, Dict[str, str], Dict[str, str]]:
    """
    Pre-processes the given Pandas DataFrame:
    1)  Add index if missing
    2a) Convert string columns to string dtype (if convert_objects)
    2b) Set content of columns of dtype other than `supported_pandas_dtypes` to supported types
        (if convert_objects & cte)
    3)  Check that the dtypes are supported
    4)  extract index_dtypes and dtypes dictionaries

    :return: Tuple:
        * Modified copy of Pandas DataFrame
        * index_dtypes dict
        * all_dtypes dict. containing index dtypes and data dtypes
    """
    index = []

    for idx, name in enumerate(df.index.names):
        if name is None:
            name = f'_index_{idx}'
        else:
            name = f'_index_{name}'

        index.append(name)

    if len(set(index)) != len(index):
        raise KeyError("index with duplicate names not supported")

    df_copy = df.copy()
    df_copy.index.set_names(index, inplace=True)
    # set the index as normal columns, this makes it easier to convert the dtype
    df_copy.reset_index(inplace=True)

    supported_pandas_dtypes = ['int64', 'float64', 'string', 'datetime64[ns]', 'bool', 'int32']
    all_dtypes = {}
    for column in df_copy.columns:
        dtype = df_copy[column].dtype.name

        if dtype in supported_pandas_dtypes:
            all_dtypes[str(column)] = dtype
            continue

        if convert_objects:
            df_copy[column] = df_copy[column].convert_dtypes(
                convert_integer=False, convert_boolean=False, convert_floating=False,
            )
            dtype = df_copy[column].dtype.name

        if dtype not in supported_pandas_dtypes and not(cte and convert_objects):
            raise TypeError(f'unsupported dtype for {column}: {dtype}')

        if cte and convert_objects:
            types = df_copy[column].apply(type).unique()
            if len(types) != 1:
                raise TypeError(f'multiple types found in column {column}: {types}')
            dtype = value_to_dtype(df_copy[column][0])

        all_dtypes[str(column)] = dtype

    index_dtypes = {index_name: all_dtypes[index_name] for index_name in index}
    return df_copy, index_dtypes, all_dtypes
