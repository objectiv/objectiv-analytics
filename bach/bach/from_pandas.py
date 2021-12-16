"""
Copyright 2021 Objectiv B.V.
"""
from typing import Tuple, Dict, List

import pandas
from sqlalchemy.engine import Engine

from bach import DataFrame, get_series_type_from_dtype
from bach.expression import Expression
from sql_models.util import quote_identifier
from bach.sql_model import BachSqlModelBuilder


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
    df_copy, index_dtypes, dtypes = _from_pd_shared(df, convert_objects)

    conn = engine.connect()
    df_copy.to_sql(name=table_name, con=conn, if_exists=if_exists, index=False)
    conn.close()

    # Todo, this should use from_table from here on.
    model_builder = BachSqlModelBuilder(sql='select * from {table_name}', name=table_name)
    model = model_builder(table_name=quote_identifier(table_name))

    # Should this also use _df_or_series?
    return DataFrame.get_instance(
        engine=engine,
        base_node=model,
        index_dtypes=index_dtypes,
        dtypes=dtypes,
        group_by=None
    )


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
    df_copy, index_dtypes, dtypes = _from_pd_shared(df, convert_objects)

    # Only support case where we have a single index column for now
    if len(index_dtypes) != 1:
        raise NotImplementedError("We only support dataframes with a single column index.")  # for now

    column_series_type = [
        get_series_type_from_dtype(dtype)
        for dtype in list(index_dtypes.values()) + list(dtypes.values())
    ]

    per_row_expr = []
    for row in df_copy.itertuples():
        per_column_expr = []
        # Access the columns in `row` by index rather than by name. Because if a name starts with an
        # underscore (e.g. _index_skating_order) it will not be available as attribute.
        # so we use `row[i]` instead of getattr(row, column_name).
        # start=1 is to account for the automatic index that pandas adds
        for i, series_type in enumerate(column_series_type, start=1):
            val = row[i]
            per_column_expr.append(series_type.value_to_expression(val))
        row_expr = Expression.construct('({})', _combine_expression(per_column_expr))
        per_row_expr.append(row_expr)
    all_values_expr = _combine_expression(per_row_expr, join_str=',\n')

    column_names = list(index_dtypes.keys()) + list(dtypes.keys())
    column_names_expr = _combine_expression(
        [Expression.raw(quote_identifier(column_name)) for column_name in column_names]
    )

    sql = 'select * from (values \n{all_values_expr}\n) as t({column_names_expr})\n'
    model_builder = BachSqlModelBuilder(sql=sql, name=name)
    model = model_builder(all_values_expr=all_values_expr, column_names_expr=column_names_expr)

    return DataFrame.get_instance(
        engine=engine,
        base_node=model,
        index_dtypes=index_dtypes,
        dtypes=dtypes,
        group_by=None
    )


def _combine_expression(expressions: List[Expression], join_str: str = ', ') -> Expression:
    fmt = join_str.join(['{}'] * len(expressions))
    return Expression.construct(fmt, *expressions)


def _from_pd_shared(
        df: pandas.DataFrame,
        convert_objects: bool
) -> Tuple[pandas.DataFrame, Dict[str, str], Dict[str, str]]:
    """
    Pre-processes the given Pandas DataFrame:
    1) Add index if missing
    2) Convert string columns to string objects (if convert_objects)
    3) Check that the dtypes are supported
    4) extract index_dtypes and dtypes dictionaries

    :return: Tuple:
        * Modified copy of Pandas DataFrame
        * index_dtypes dict
        * dtypes dict
    """
    if df.index.name is None:  # for now only one index allowed todo check this
        index = '_index_0'
    else:
        index = f'_index_{df.index.name}'
    # set the index as a normal column, this makes it easier to convert the dtype
    df_copy = df.rename_axis(index).reset_index()
    if convert_objects:
        df_copy = df_copy.convert_dtypes(convert_integer=False,
                                         convert_boolean=False,
                                         convert_floating=False)
    # todo add support for 'timedelta64[ns]'. pd.to_sql writes timedelta as bigint to sql, so
    # not implemented yet
    supported_types = ['int64', 'float64', 'string', 'datetime64[ns]', 'bool']
    index_dtype = df_copy[index].dtype.name
    if index_dtype not in supported_types:
        raise ValueError(f"index is of type '{index_dtype}', should one of {supported_types}. "
                         f"For 'object' columns convert_objects=True can be used to convert these columns"
                         f"to type 'string'.")
    index_dtypes = {index: index_dtype}
    dtypes = {str(column_name): dtype.name for column_name, dtype in df_copy.dtypes.items()
              if column_name in df.columns}
    unsupported_dtypes = {str(column_name): dtype for column_name, dtype in dtypes.items()
                          if dtype not in supported_types}
    if unsupported_dtypes:
        raise ValueError(f"dtypes {unsupported_dtypes} are not supported, should one of "
                         f"{supported_types}. "
                         f"For 'object' columns convert_objects=True can be used to convert these columns"
                         f"to type 'string'.")
    return df_copy, index_dtypes, dtypes
