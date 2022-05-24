"""
Copyright 2021 Objectiv B.V.
"""
from typing import Tuple, Dict, Set

import numpy
import pandas
from sqlalchemy.engine import Engine, Dialect

from bach import DataFrame, get_series_type_from_dtype
from bach.types import value_to_dtype, DtypeOrAlias, Dtype
from bach.expression import Expression, join_expressions
from bach.utils import is_valid_column_name
from sql_models.model import CustomSqlModelBuilder
from sql_models.util import quote_identifier, DatabaseNotSupportedException, is_postgres, is_bigquery


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
    df_copy, index_dtypes, all_dtypes = _from_pd_shared(
        dialect=engine.dialect,
        df=df,
        convert_objects=convert_objects,
        cte=False
    )

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
    using a `select * from values()` query, or something similar depending on the database dialect.

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
    df_copy, index_dtypes, all_dtypes = _from_pd_shared(
        dialect=engine.dialect,
        df=df,
        convert_objects=convert_objects,
        cte=True
    )

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
            per_column_expr.append(
                series_type.value_to_expression(dialect=engine.dialect, value=val, dtype=series_type.dtype)
            )
        row_expr = Expression.construct('({})', join_expressions(per_column_expr))
        per_row_expr.append(row_expr)
    all_values_str = join_expressions(per_row_expr, join_str=',\n').to_sql(engine.dialect)

    if is_postgres(engine):
        # We are building sql of the form:
        #     select * from (values
        #         ('row 1', cast(1234 as bigint), cast(-13.37 as double precision)),
        #         ('row 2', cast(1337 as bigint), cast(31.337 as double precision))
        #     ) as t("a", "b", "c")
        column_names_expr = join_expressions(
            [Expression.raw(quote_identifier(engine.dialect, column_name)) for column_name in
             all_dtypes.keys()]
        )
        column_names_str = column_names_expr.to_sql(engine.dialect)
        sql = f'select * from (values \n{all_values_str}\n) as t({column_names_str})\n'
    elif is_bigquery(engine):
        # We are building sql of the form:
        #     select * from UNNEST([
        #         STRUCT<`a` STRING, `b` INT64, `c` FLOAT64>
        #         ('row 1', 1234, cast(-13.37 as FLOAT64))
        #         ('row 2', 1337, cast(31.337 as FLOAT64))
        #     ])
        sql_column_name_types = []
        for col_name, dtype in all_dtypes.items():
            db_col_name = quote_identifier(dialect=engine.dialect, name=col_name)
            db_dtype = get_series_type_from_dtype(dtype).get_db_dtype(dialect=engine.dialect)
            sql_column_name_types.append(f'{db_col_name} {db_dtype}')
        sql_struct = f'STRUCT<{", ".join(sql_column_name_types)}>'
        sql = f'select * from UNNEST([{sql_struct} \n{all_values_str}\n])\n'
    else:
        raise DatabaseNotSupportedException(engine)

    model_builder = CustomSqlModelBuilder(sql=sql, name=name)
    sql_model = model_builder()

    index = list(index_dtypes.keys())
    return DataFrame.from_model(engine=engine, model=sql_model, index=index, all_dtypes=all_dtypes)


def _assert_column_names_valid(dialect: Dialect, df: pandas.DataFrame):
    """
    Performs three checks on the columns (not on the indices) of the DataFrame:
    1) All Series must have a string as name
    2) No duplicated Series names
    3) All Series names are valid column names in the given sql dialect
    Will raise a ValueError if any of the checks fails
    """
    names = list(df.columns)
    not_strings = [name for name in names if not isinstance(name, str)]
    if not_strings:
        raise ValueError(f'Not all columns names are strings. Non-string names: {not_strings}')
    if len(set(names)) != len(names):
        raise ValueError(f'Duplicate column names in: {names}')

    invalid_column_names = [name for name in names if not is_valid_column_name(dialect=dialect, name=name)]
    if invalid_column_names:
        raise ValueError(f'Invalid column names: {invalid_column_names} for SQL dialect {dialect} ')


def _from_pd_shared(
        dialect: Dialect,
        df: pandas.DataFrame,
        convert_objects: bool,
        cte: bool
) -> Tuple[pandas.DataFrame, Dict[str, Dtype], Dict[str, Dtype]]:
    """
    Pre-processes the given Pandas DataFrame, and do some checks. This results in a new DataFrame and two
    dictionaries with meta data. The returned DataFrame contains all processed data in the data columns, this
    includes any columns that were originally indices. The index_dtypes dict will indicate which of the data
    columns should be indexes.

    Pre-processing/checks:
    1)  Add index if missing
    2a) Convert string columns to string dtype (if convert_objects)
    2b) Set content of columns of dtype other than `supported_pandas_dtypes` to supported types
        (if convert_objects & cte)
    3)  Check that the dtypes are supported
    4)  extract index_dtypes and dtypes dictionaries
    5) Check: all column names (after previous steps) are set, unique, and are valid column names for the
        given sql dialect.

    :return: Tuple:
        * Modified copy of Pandas DataFrame.
        * index_dtypes dict. Mapping of index names to the dtype.
        * all_dtypes dict. Mapping of all columns names to dtypes, includes data and index columns.
    """
    index = []

    for idx, name in enumerate(df.index.names):
        if name is None:
            name = f'_index_{idx}'
        else:
            name = f'_index_{name}'

        index.append(name)

    df_copy = df.copy()
    df_copy.index.set_names(index, inplace=True)
    # set the index as normal columns, this makes it easier to convert the dtype
    df_copy.reset_index(inplace=True)

    supported_pandas_dtypes = ['int64', 'float64', 'string', 'datetime64[ns]', 'bool', 'int32']
    all_dtypes_or_alias: Dict[str, DtypeOrAlias] = {}
    for column in df_copy.columns:
        dtype = df_copy[column].dtype.name

        if dtype in supported_pandas_dtypes:
            all_dtypes_or_alias[str(column)] = dtype
            continue

        if df_copy[column].dropna().empty:
            raise ValueError(f'{column} column has no non-nullable values, cannot infer type.')

        if convert_objects:
            df_copy[column] = df_copy[column].convert_dtypes(
                convert_integer=False, convert_boolean=False, convert_floating=False,
            )
            dtype = df_copy[column].dtype.name

        if dtype not in supported_pandas_dtypes and not(cte and convert_objects):
            raise TypeError(f'unsupported dtype for {column}: {dtype}')

        if cte and convert_objects:
            non_nullables = df_copy[column].dropna()
            types = non_nullables.apply(type).unique()
            if len(types) != 1:
                raise TypeError(f'multiple types found in column {column}: {types}')
            dtype = value_to_dtype(non_nullables.iloc[0])

        all_dtypes_or_alias[str(column)] = dtype

    _assert_column_names_valid(dialect=dialect, df=df_copy)

    all_dtypes = {name: get_series_type_from_dtype(dtype_or_alias).dtype
                  for name, dtype_or_alias in all_dtypes_or_alias.items()}
    index_dtypes = {index_name: all_dtypes[index_name] for index_name in index}

    df_copy = df_copy.replace({numpy.nan: None})
    return df_copy, index_dtypes, all_dtypes
