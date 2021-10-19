import datetime
import json
from abc import abstractmethod, ABC
from copy import copy
from typing import List, Set, Union, Dict, Any, Optional, Tuple, cast, Type, NamedTuple, TYPE_CHECKING
from uuid import UUID

import numpy
import pandas
from sqlalchemy.engine import Engine

from buhtuh.expression import Expression
from buhtuh.types import get_series_type_from_dtype, value_to_dtype, get_dtype_from_db_dtype
from sql_models.model import SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql
from buhtuh.json import Json

if TYPE_CHECKING:
    from buhtuh.partitioning import BuhTuhWindow, BuhTuhGroupBy


DataFrameOrSeries = Union['BuhTuhDataFrame', 'BuhTuhSeries']
ColumnNames = Union[str, List[str]]


class SortColumn(NamedTuple):
    # todo: use Expression?
    expression: str
    asc: bool


class BuhTuhDataFrame:
    """
    A mutable DataFrame representing tabular data in a database and enabling operations on that data.

    The data of this DataFrame is always held in the database and operations on the data are performed
    by the database, not in local memory. Data will only be transferred to local memory when an
    explicit call is made to one of the functions that transfers data:
    * head()
    * to_df()
    Other functions will not transfer data, nor will they trigger any operations to run on the database.
    Operations on the DataFrame are combined and translated to a single SQL query, which is executed
    only when one of the above mentioned data-transfer functions is called.

    The initial data of the DataFrame is the result of the SQL query that the `base_node` parameter
    contains. That can be a simple query on a table, but also a complicated query in itself. Operations
    on the data will result in SQL queries that build on top of the query of the base_node. The
    index and series parameters contain meta information about the data in the base_node.

    The API of this DataFrame is partially compatible with Pandas DataFrames. For more on Pandas
    DataFrames see https://pandas.pydata.org/docs/reference/frame.html
    """
    def __init__(
        self,
        engine: Engine,
        base_node: SqlModel,
        index: Dict[str, 'BuhTuhSeries'],
        series: Dict[str, 'BuhTuhSeries'],
        order_by: List[SortColumn] = None
    ):
        """
        Instantiate a new BuhTuhDataFrame.
        There are utility class methods to easily create a BuhTuhDataFrame from existing data such as a
        table (`from_table()`) or already instantiated sql-model (`from_model()`).

        :param engine: db connection
        :param base_node: sql-model of a select statement that must contain all columns/expressions that
            are present in the series parameter.
        :param index: Dictionary mapping the name of each index-column to a Series object representing
            the column.
        :param series: Dictionary mapping the name of each data-column to a Series object representing
            the column.
        :param order_by: Optional list of sort-columns to order the DataFrame by
        """
        self._engine = engine
        self._base_node = base_node
        self._index = copy(index)
        self._data: Dict[str, BuhTuhSeries] = {}
        self._order_by = order_by if order_by is not None else []
        for key, value in series.items():
            if key != value.name:
                raise ValueError(f'Keys in `series` should match the name of series. '
                                 f'key: {key}, series.name: {value.name}')
            self._data[key] = value
        if set(index.keys()) & set(series.keys()):
            raise ValueError(f"The names of the index series and data series should not intersect. "
                             f"Index series: {sorted(index.keys())} data series: {sorted(series.keys())}")

    def copy_override(
            self,
            engine: Engine = None,
            base_node: SqlModel = None,
            index: Dict[str, 'BuhTuhSeries'] = None,
            series: Dict[str, 'BuhTuhSeries'] = None,
            order_by: List[SortColumn] = None) -> 'BuhTuhDataFrame':
        """
        Create a copy of self, with the given arguments overriden
        """
        return BuhTuhDataFrame(
            engine=engine if engine is not None else self.engine,
            base_node=base_node if base_node is not None else self._base_node,
            index=index if index is not None else self._index,
            series=series if series is not None else self._data,
            order_by=order_by if order_by is not None else self._order_by
        )

    @property
    def engine(self):
        return self._engine

    @property
    def base_node(self) -> SqlModel:
        return self._base_node

    @property
    def index(self) -> Dict[str, 'BuhTuhSeries']:
        return copy(self._index)

    @property
    def data(self) -> Dict[str, 'BuhTuhSeries']:
        return copy(self._data)

    @property
    def all_series(self) -> Dict[str, 'BuhTuhSeries']:
        return {**self.index, **self.data}

    @property
    def index_columns(self) -> List[str]:
        return list(self.index.keys())

    @property
    def data_columns(self) -> List[str]:
        return list(self.data.keys())

    @property
    def index_dtypes(self):
        return {column: data.dtype for column, data in self.index.items()}

    @property
    def dtypes(self):
        return {column: data.dtype for column, data in self.data.items()}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BuhTuhDataFrame):
            return False
        # We cannot just compare the data and index properties, because the BuhTuhSeries objects have
        # overridden the __eq__ function in a way that makes normal comparisons not useful. We have to use
        # equals() instead
        if list(self.index.keys()) != list(other.index.keys()):
            return False
        if list(self.data.keys()) != list(other.data.keys()):
            return False
        for key in self.all_series.keys():
            if not self.all_series[key].equals(other.all_series[key]):
                return False
        return \
            self.engine == other.engine and \
            self.base_node == other.base_node and \
            self._order_by == other._order_by

    @classmethod
    def _get_dtypes(cls, engine: Engine, node: SqlModel) -> Dict[str, str]:
        new_node = CustomSqlModel(sql='select * from {{previous}} limit 0')(previous=node)
        select_statement = to_sql(new_node)
        sql = f"""
            create temporary table tmp_table_name on commit drop as
            ({select_statement});
            select column_name, data_type
            from information_schema.columns
            where table_name = 'tmp_table_name'
            order by ordinal_position;
        """
        with engine.connect() as conn:
            res = conn.execute(sql)
        return {x[0]: get_dtype_from_db_dtype(x[1]) for x in res.fetchall()}

    @classmethod
    def from_table(cls, engine, table_name: str, index: List[str]) -> 'BuhTuhDataFrame':
        """
        Instantiate a new BuhTuhDataFrame based on the content of an existing table in the database.
        This will create and remove a temporary table to asses meta data.
        """
        # todo: don't create a temporary table, the real table (and its meta data) already exists
        model = CustomSqlModel(sql=f'SELECT * FROM {table_name}').instantiate()
        return cls._from_node(engine, model, index)

    @classmethod
    def from_model(cls, engine, model: SqlModel, index: List[str]) -> 'BuhTuhDataFrame':
        """
        Instantiate a new BuhTuhDataFrame based on the result of the query defines in `model`
        :param engine: db connection
        :param model: sql model.
        :param index: list of column names that make up the index.
        """
        # Wrap the model in a simple select, so we know for sure that the top-level model has no unexpected
        # select expressions, where clauses, or limits
        wrapped_model = CustomSqlModel(sql='SELECT * FROM {{model}}')(model=model)
        return cls._from_node(engine, wrapped_model, index)

    @classmethod
    def _from_node(cls, engine, model: SqlModel, index: List[str]) -> 'BuhTuhDataFrame':
        dtypes = cls._get_dtypes(engine, model)

        index_dtypes = {k: dtypes[k] for k in index}
        series_dtypes = {k: dtypes[k] for k in dtypes.keys() if k not in index}

        # Should this also use _df_or_series?
        return cls.get_instance(
            engine=engine,
            base_node=model,
            index_dtypes=index_dtypes,
            dtypes=series_dtypes,
            order_by=[]
        )

    @classmethod
    def from_dataframe(cls,
                       df: pandas.DataFrame,
                       name: str,
                       engine: Engine,
                       convert_objects: bool = False,
                       if_exists: str = 'fail'):
        """
        Instantiate a new BuhTuhDataFrame based on the content of a Pandas DataFrame. Supported dtypes are
        'int64', 'float64', 'string', 'datetime64[ns]', 'bool'
        This will first load the data into the database using pandas' df.to_sql() method.

        :param df: Pandas DataFrame to instantiate as BuhTuhDataFrame
        :param name: name of the sql table the Pandas DataFrame will be written to
        :param engine: db connection
        :param convert_objects: If True, columns of type 'object' are converted to 'string' using the
            pd.convert_dtypes() method where possible.
        :param if_exists: {'fail', 'replace', 'append'}, default 'fail'
            How to behave if the table already exists.

            * fail: Raise a ValueError.
            * replace: Drop the table before inserting new values.
            * append: Insert new values to the existing table.
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
        dtypes = {column_name: dtype.name for column_name, dtype in df_copy.dtypes.items()
                  if column_name in df.columns}
        unsupported_dtypes = {column_name: dtype for column_name, dtype in dtypes.items()
                              if dtype not in supported_types}
        if unsupported_dtypes:
            raise ValueError(f"dtypes {unsupported_dtypes} are not supported, should one of "
                             f"{supported_types}. "
                             f"For 'object' columns convert_objects=True can be used to convert these columns"
                             f"to type 'string'.")

        # todo add dtypes argument that explicitly let's you set the supported dtypes for pandas columns
        conn = engine.connect()
        df_copy.to_sql(name=name, con=conn, if_exists=if_exists, index=False)
        conn.close()

        # Todo, this should use from_table from here on.
        model = CustomSqlModel(sql=f'SELECT * FROM {name}').instantiate()

        # Should this also use _df_or_series?
        return cls.get_instance(
            engine=engine,
            base_node=model,
            index_dtypes={index: index_dtype},
            dtypes=dtypes
        )

    @classmethod
    def get_instance(
            cls,
            engine,
            base_node: SqlModel,
            index_dtypes: Dict[str, str],
            dtypes: Dict[str, str],
            order_by: List[SortColumn] = None
    ) -> 'BuhTuhDataFrame':
        """
        Get an instance with the right series instantiated based on the dtypes array. This assumes that
        base_node has a column for all names in index_dtypes and dtypes.
        """

        index: Dict[str, BuhTuhSeries] = {}
        for key, value in index_dtypes.items():
            index_type = get_series_type_from_dtype(value)
            index[key] = index_type(
                engine=engine,
                base_node=base_node,
                index=None,  # No index for index
                name=key
            )
        series: Dict[str, BuhTuhSeries] = {}
        for key, value in dtypes.items():
            series_type = get_series_type_from_dtype(value)
            series[key] = series_type(
                engine=engine,
                base_node=base_node,
                index=index,
                name=key
            )
        return BuhTuhDataFrame(
            engine=engine,
            base_node=base_node,
            index=index,
            series=series,
            order_by=order_by
        )

    def _df_or_series(self, df: 'BuhTuhDataFrame') -> DataFrameOrSeries:
        """
        Figure out whether there is just one series in our data, and return that series instead of the
        whole frame.
        :param df: the df
        :return: BuhTuhDataFrame, BuhTuhSeries
        """
        if len(df.data) > 1:
            return df
        return list(df.data.values())[0]

    def get_df_materialized_model(self) -> 'BuhTuhDataFrame':
        """
        Create a copy of this DataFrame with as base_node the current DataFrame's state.

        This effectively adds a node to the underlying SqlModel graph. Generally adding nodes increases
        the size of the generated SQL query. But this can be useful if the current DataFrame contains
        expressions that you want to evaluate before further expressions are build on top of them. This might
        make sense for very large expressions, or for non-deterministic expressions (e.g. see
        BuhTuhSeriesUuid.sql_gen_random_uuid()).

        :return: New DataFrame with the current DataFrame's state as base_node
        """
        model = self.get_current_node()
        index_dtypes = {k: v.dtype for k, v in self.index.items()}
        series_dtypes = {k: v.dtype for k, v in self.data.items()}

        return self.get_instance(
            engine=self.engine,
            base_node=model,
            index_dtypes=index_dtypes,
            dtypes=series_dtypes,
            order_by=[]
        )

    def __getitem__(self,
                    key: Union[str, List[str], Set[str], slice, 'BuhTuhSeriesBoolean']) -> DataFrameOrSeries:
        """
        TODO: Comments
        :param key:
        :return:
        """

        if isinstance(key, str):
            return self.data[key]
        if isinstance(key, (set, list)):
            key_set = set(key)
            if not key_set.issubset(set(self.data_columns)):
                raise KeyError(f"Keys {key_set.difference(set(self.data_columns))} not in data_columns")
            selected_data = {key: data for key, data in self.data.items() if key in key_set}

            return self.copy_override(series=selected_data)

        if isinstance(key, slice):
            model = self.get_current_node(limit=key)
            return self._df_or_series(df=self.copy_override(base_node=model))

        if isinstance(key, BuhTuhSeriesBoolean):
            # We only support first level boolean indices for now
            if key.base_node != self.base_node:
                raise ValueError('Cannot apply Boolean series with a different base_node to DataFrame.'
                                 'Hint: make sure the Boolean series is derived from this DataFrame. '
                                 'Alternative: use df.merge(series) to merge the series with the df first,'
                                 'and then create a new Boolean series on the resulting merged data.')
            model_builder = CustomSqlModel(
                name='boolean_selection',
                sql='select {index_str}, {columns_sql_str} from {{_last_node}} where {where}'
            )
            model = model_builder(
                columns_sql_str=self._get_all_column_expressions(),
                index_str=', '.join(self.index.keys()),
                _last_node=self.base_node,
                where=key.get_expression(),
            )
            return self._df_or_series(
                BuhTuhDataFrame.get_instance(
                    engine=self.engine,
                    base_node=model,
                    index_dtypes={name: series.dtype for name, series in self.index.items()},
                    dtypes={name: series.dtype for name, series in self.data.items()},
                    order_by=[]  # filtering rows resets any sorting
                )
            )
        raise NotImplementedError(f"Only str, (set|list)[str], slice or BuhTuhSeriesBoolean are supported, "
                                  f"but got {type(key)}")

    def __getattr__(self, attr):
        return self._data[attr]

    def __setitem__(self,
                    key: Union[str, List[str]],
                    value: Union['BuhTuhSeries', int, str, float, UUID]):
        """
        TODO: Comments
        """
        # TODO: all types from types.TypeRegistry are supported.
        if isinstance(key, str):
            if not isinstance(value, BuhTuhSeries):
                series = const_to_series(base=self, value=value, name=key)
                self._data[key] = series
                return
            else:
                # two cases:
                # 1) these share the same base_node and index
                # 2) these share the same index, but not the same base_node
                if value.index != self.index:
                    raise ValueError(f'Index of assigned value does not match index of DataFrame. '
                                     f'Value: {value.index}, df: {self.index}')
                if value.base_node == self.base_node:
                    self._data[key] = BuhTuhSeries.get_instance(
                        base=self,
                        name=key,
                        dtype=value.dtype,
                        expression=value.expression
                    )
                    return
                else:
                    # this is the complex case. Maybe don't support this at all?TODO
                    raise NotImplementedError('TODO')

        elif isinstance(key, list):
            if len(key) == 0:
                return
            if len(key) == 1:
                return self.__setitem__(key[0], value)
            # len(key) > 1
            if not isinstance(value, BuhTuhDataFrame):
                raise ValueError(f'Assigned value should be a BuhTuhDateFrame, provided: {type(value)}')
            if len(value.data_columns) != len(key):
                raise ValueError(f'Number of columns in key and value should match. '
                                 f'Key: {len(key)}, value: {len(value.data_columns)}')
            series_list = [value.data[col_name] for col_name in value.data_columns]
            for i, sub_key in enumerate(key):
                self.__setitem__(sub_key, series_list[i])
        else:
            raise ValueError(f'Key should be either a string or a list of strings, value: {key}')

    def __delitem__(self, key: str):
        """ TODO: comments """
        if isinstance(key, str):
            del(self._data[key])
            return
        else:
            raise TypeError(f'Unsupported type {type(key)}')

    def astype(self, dtype: Union[str, Dict[str, str]]) -> 'BuhTuhDataFrame':
        """
        Cast all or some of the data columns to a certain type.

        Only data columns can be cast, index columns cannot be cast.

        This does not modify the current DataFrame, instead it returns a new DataFrame.
        :param dtype: either
            * A single str, in which case all data columns are cast to this dtype
            * A dictionary mapping column labels to dtype.
        :return: New DataFrame with the specified column(s) cast to the specified type
        """
        # Check and/or convert parameters
        if not isinstance(dtype, dict):
            dtype = {column: dtype for column in self.data_columns}
        not_existing_columns = set(dtype.keys()) - set(self.data_columns)
        if not_existing_columns:
            raise ValueError(f'Specified columns do not exist: {not_existing_columns}')

        # Construct new dataframe with converted columns
        new_data = {}
        for column, series in self.data.items():
            new_dtype = dtype.get(column)
            if new_dtype:
                new_data[column] = series.astype(dtype=new_dtype)
            else:
                new_data[column] = series

        return self.copy_override(series=new_data)

    def _partition_by_columns(self, by: Union[str, 'BuhTuhSeries', List[str], List['BuhTuhSeries'], None]
                              ) -> List['BuhTuhSeries']:
        """
        Helper method to check and compile a partitioning list
        """
        group_by_columns: List['BuhTuhSeries'] = []
        if isinstance(by, str):
            group_by_columns.append(self.all_series[by])
        elif isinstance(by, BuhTuhSeries):
            group_by_columns.append(by)
        elif isinstance(by, list):
            for by_item in by:
                if isinstance(by_item, str):
                    group_by_columns.append(self.all_series[by_item])
                if isinstance(by_item, BuhTuhSeries):
                    group_by_columns.append(by_item)
        elif by is None:
            pass
        else:
            raise ValueError(f'Value of "by" should be either None, a string, or a Series.')

        return group_by_columns

    def groupby(
            self,
            by: Union[str, 'BuhTuhSeries', List[str], List['BuhTuhSeries'], None] = None
    ) -> 'BuhTuhGroupBy':
        """
        Group by any of the series currently in this dataframe, both from index
        as well as data.
        :param by: The series to group by
        :return: an object to perform aggregations on
        """
        from buhtuh.partitioning import BuhTuhGroupBy
        return BuhTuhGroupBy(buh_tuh=self.copy_override(), group_by_columns=self._partition_by_columns(by))

    def window(self,
               by: Union[str, 'BuhTuhSeries', List[str], List['BuhTuhSeries'], None] = None,
               **frame_args):
        """
        Create a window on the current dataframe and its sorting.
        TODO Better argument typing, needs fancy import logic
        :see: BuhTuhWindow __init__ for frame args
        """
        from buhtuh.partitioning import BuhTuhWindow
        return BuhTuhWindow(buh_tuh=self.copy_override(),
                            group_by_columns=self._partition_by_columns(by),
                            **frame_args)

    def sort_values(
            self,
            by: Union[str, List[str]],
            ascending: Union[bool, List[bool]] = True
    ) -> 'BuhTuhDataFrame':
        """
        Create a new DataFrame with the specified sorting order.

        This does not modify the current DataFrame, instead it returns a new DataFrame.

        The sorting will remain in the returned DataFrame as long as no operations are performed on that
        frame that materially change the selected data. Operations that materially change the selected data
        are for example groupby(), merge(), get_df_materialized_model(), and filtering out rows. Adding or
        removing a column does not materially change the selected data.

        :param by: column label or list of labels to sort by.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            by must also be a list and len(ascending) == len(by)
        :return: a new DataFrame with the specified ordering
        """
        if isinstance(by, str):
            by = [by]
        elif not isinstance(by, list) or not all(isinstance(by_item, str) for by_item in by):
            raise TypeError('by should be a str, or a list of str')
        if isinstance(ascending, bool):
            ascending = [ascending] * len(by)
        if len(by) != len(ascending):
            raise ValueError(f'Length of ascending ({len(ascending)}) != length of by ({len(by)})')
        missing = set(by) - set(self.all_series.keys())
        if len(missing) > 0:
            raise KeyError(f'Some series could not be found in current frame: {missing}')

        by_series_list = [self.all_series[by_name] for by_name in by]
        order_by = [SortColumn(expression=by_series.get_expression(), asc=asc_item)
                    for by_series, asc_item in zip(by_series_list, ascending)]
        return self.copy_override(order_by=order_by)

    def to_df(self) -> pandas.DataFrame:
        """
        Run a SQL query representing the current state of this DataFrame against the database and return the
        resulting data as a Pandas DataFrame.

        This function queries the database.
        """
        conn = self.engine.connect()
        sql = self.view_sql()
        df = pandas.read_sql_query(sql, conn, index_col=list(self.index.keys()))
        conn.close()
        return df

    def head(self, n: int = 5) -> pandas.DataFrame:
        """
        Similar to `to_df` but only returns the first `n` rows.

        This function queries the database.

        :param n: number of rows to query from database.
        """
        conn = self.engine.connect()
        sql = self.view_sql(limit=n)
        df = pandas.read_sql_query(sql, conn, index_col=list(self.index.keys()))
        conn.close()
        return df

    def get_order_by_expression(self):
        """
        Get a properly formatted order by expression based on this df's order_by.
        Will return an empty string in case ordering in not requested.
        """
        if self._order_by:
            order_str = ", ".join(f"{sc.expression} {'asc' if sc.asc else 'desc'}" for sc in self._order_by)
            order_str = f'order by {order_str}'
        else:
            order_str = ''

        return order_str

    def get_current_node(self, limit: Union[int, slice] = None) -> SqlModel[CustomSqlModel]:
        """
        Translate the current state of this DataFrame into a SqlModel.
        :param limit: The limit to use
        :return: SQL query as a SqlModel that represents the current state of this DataFrame.
        """

        if isinstance(limit, int):
            limit = slice(0, limit)

        limit_str = 'limit all'
        if limit is not None:
            if limit.step is not None:
                raise NotImplementedError("Step size not supported in slice")
            if (limit.start is not None and limit.start < 0) or \
                    (limit.stop is not None and limit.stop < 0):
                raise NotImplementedError("Negative start or stop not supported in slice")

            if limit.start is not None:
                if limit.stop is not None:
                    if limit.stop <= limit.start:
                        raise ValueError('limit.stop <= limit.start')
                    limit_str = f'limit {limit.stop - limit.start} offset {limit.start}'
                else:
                    limit_str = f'limit all offset {limit.start}'
            else:
                if limit.stop is not None:
                    limit_str = f'limit {limit.stop}'

        model_builder = CustomSqlModel(
            name='view_sql',
            sql='select {index_str}, {columns_sql_str} from {{_last_node}} {order} {limit}'
        )

        return model_builder(
            columns_sql_str=self._get_all_column_expressions(),
            index_str=', '.join(f'"{index_column}"' for index_column in self.index.keys()),
            _last_node=self.base_node,
            limit='' if limit_str is None else f'{limit_str}',
            order=self.get_order_by_expression()
        )

    def view_sql(self, limit: Union[int, slice] = None) -> str:
        """
        Translate the current state of this DataFrame into a SQL query.
        :param limit: limit on which rows to select in the query
        :return: SQL query
        """
        model = self.get_current_node(limit=limit)
        sql = to_sql(model)
        return sql

    def _get_all_column_expressions(self, table_alias=''):
        column_expressions = []
        for column in self.data_columns:
            series = self.data[column]
            column_expressions.append(series.get_column_expression(table_alias))
        return ', '.join(column_expressions)

    def merge(
            self,
            right: DataFrameOrSeries,
            how: str = 'inner',
            on: ColumnNames = None,
            left_on: ColumnNames = None,
            right_on: ColumnNames = None,
            left_index: bool = False,
            right_index: bool = False,
            suffixes: Tuple[str, str] = ('_x', '_y'),
    ) -> 'BuhTuhDataFrame':
        """
        Join the right Dataframe or Series on self. This will return a new DataFrame that contains the
        combined columns of both dataframes, and the rows that result from joining on the specified columns.
        The columns that are joined on can consist (partially or fully) out of index columns.

        See buhtuh.merge.merge() for more information.
        The interface of this function is similar to pandas' merge, but the following parameters are not
        supported: sort, copy, indicator, and validate.
        Additionally when merging two frames that have conflicting columns names, and joining on indices,
        then the resulting columns/column names can differ slightly from Pandas.
        """
        from buhtuh.merge import merge
        return merge(
            left=self,
            right=right,
            how=how,
            on=on,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            suffixes=suffixes
        )


class BuhTuhSeries(ABC):
    """
    Immutable class representing a column/expression in a query.
    """
    def __init__(self,
                 engine,
                 base_node: SqlModel,
                 index: Optional[Dict[str, 'BuhTuhSeries']],
                 name: str,
                 expression: Expression = None,
                 sorted_ascending: Optional[bool] = None):
        """
        TODO: docstring
        :param engine:
        :param base_node:
        :param index: None if this Series is part of an index. Otherwise a dict with the Series that are
                        this Series' index
        :param name:
        :param expression:
        :param sorted_ascending: None for no sorting, True for sorted ascending, False for sorted descending
        """
        self._engine = engine
        self._base_node = base_node
        self._index = index
        self._name = name
        # todo: change expression in an ast-like object, that can be a constant, column, operator, and/or
        #   refer other series
        if expression:
            self._expression = expression
        else:
            self._expression = Expression.construct_table_field(self.name)
        self._sorted_ascending = sorted_ascending

    @property
    @classmethod
    @abstractmethod
    def dtype(cls) -> str:
        """
        The dtype of this BuhTuhSeries. The dtype is used to uniquely identify data of the type that is
        represented by this BuhTuhSeries subclass. The dtype should be unique among all BuhTuhSeries
        subclasses.
        """
        raise NotImplementedError()

    @property
    @classmethod
    def dtype_aliases(cls) -> Tuple[Union[Type, str], ...]:
        """
        One or more aliases for the dtype.
        For example a BuhTuhBooleanSeries might have dtype 'bool', and as an alias the string 'boolean' and
        the builtin `bool`. An alias can be used in a similar way as the real dtype, e.g. to cast data to a
        certain type: `x.astype('boolean')` is the same as `x.astype('bool')`.

        Subclasses can override this value to indicate what strings they consider aliases for their dtype.
        """
        return tuple()

    @property
    @classmethod
    def supported_db_dtype(cls) -> Optional[str]:
        """
        Database level data type, that can be expressed using this BuhTuhSeries type.
        Example: 'double precision' for a float in Postgres

        Subclasses should override this value if they intend to be the default class to handle such types.
        When creating a BuhTuhDataFrame from existing data in a database, this field will be used to
        determine what BuhTuhSeries to instantiate for a column.
        """
        return None

    @property
    @classmethod
    def supported_value_types(cls) -> Tuple[Type, ...]:
        """
        List of python types that can be converted to database values using the `value_to_sql()` method.

        Subclasses can override this value to indicate what types are supported by value_to_sql().
        """
        return tuple()

    @classmethod
    @abstractmethod
    def value_to_sql(cls, value: Any) -> str:
        """
        Give the sql expression for the given value.
        :return: sql expression of the value
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_dtype_to_sql(cls, source_dtype: str, expression: Expression) -> Expression:
        """
        Give the sql expression to convert the given expression, of the given source dtype to the dtype of
        this Series.
        :return: sql expression
        """
        raise NotImplementedError()

    @property
    def engine(self):
        return self._engine

    @property
    def base_node(self) -> SqlModel:
        return self._base_node

    @property
    def index(self) -> Optional[Dict[str, 'BuhTuhSeries']]:
        return copy(self._index)

    @property
    def name(self) -> str:
        return self._name

    @property
    def expression(self) -> Expression:
        return self._expression

    def head(self, n: int = 5):
        """
        Return the first `n` rows.
        """
        # TODO get a series directly instead of ripping it out of the df?
        return self.to_frame().head(n)[self.name]

    def sort_values(self, ascending=True):
        """
        Returns a copy of this Series that is sorted by its values. Returns self if self is already sorted
        in that way.
        :param ascending: Whether to sort ascending (True) or descending (False)
        """
        if self._sorted_ascending is not None and self._sorted_ascending == ascending:
            return self
        return self.get_class_instance(
            base=self,
            name=self.name,
            expression=self.expression,
            sorted_ascending=ascending
        )

    def view_sql(self):
        return self.to_frame().view_sql()

    def to_frame(self) -> BuhTuhDataFrame:
        if self.index is None:
            raise Exception('to_frame() is not supported for Series that do not have an index')
        if self._sorted_ascending is not None:
            order_by = [SortColumn(expression=self.get_expression(), asc=self._sorted_ascending)]
        else:
            order_by = []
        return BuhTuhDataFrame(
            engine=self.engine,
            base_node=self.base_node,
            index=self.index,
            series={self.name: self},
            order_by=order_by
        )

    @classmethod
    def get_instance(
            cls,
            base: DataFrameOrSeries,
            name: str,
            dtype: str,
            expression: Expression = None,
            sorted_ascending: Optional[bool] = None
    ) -> 'BuhTuhSeries':
        """
        Create an instance of the right sub-class of BuhTuhSeries.
        The subclass is based on the provided dtype. See docstring of __init__ for other parameters.
        """
        series_type = get_series_type_from_dtype(dtype=dtype)
        return series_type.get_class_instance(
            base=base,
            name=name,
            expression=expression,
            sorted_ascending=sorted_ascending
        )

    @classmethod
    def get_class_instance(
            cls,
            base: DataFrameOrSeries,
            name: str,
            expression: Expression = None,
            sorted_ascending: Optional[bool] = None
    ):
        """ Create an instance of this class. """
        return cls(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=expression,
            sorted_ascending=sorted_ascending
        )

    def get_expression(self, table_alias='') -> str:
        return self.expression.to_string(table_alias)
        # # TODO BLOCKER! escape the stuff
        #
        # if table_alias != '' and table_alias[-1] != '.':
        #     table_alias = table_alias + '.'
        #
        # return self.expression.format(table_alias=table_alias)

    def get_column_expression(self, table_alias='') -> str:
        # TODO BLOCKER! escape the stuff
        expression = self.get_expression(table_alias)
        if expression != self.name:
            return f'{expression} as "{self.name}"'
        else:
            return expression

    def _check_supported(self, operation_name: str, supported_dtypes: List[str], other: 'BuhTuhSeries'):

        if self.base_node != other.base_node:
            raise ValueError(f'Cannot apply {operation_name} on two series with different base_node. '
                             f'Hint: make sure both series belong to or are derived from the same '
                             f'DataFrame. '
                             f'Alternative: use merge() to create a DataFrame with both series. ')

        if other.dtype.lower() not in supported_dtypes:
            raise TypeError(f'{operation_name} not supported between {self.dtype} and {other.dtype}.')

    def _get_derived_series(self, new_dtype: str, expression: Expression):
        return BuhTuhSeries.get_instance(
            base=self,
            name=self.name,
            dtype=new_dtype,
            expression=expression
        )

    def astype(self, dtype: Union[str, Type]) -> 'BuhTuhSeries':
        if dtype == self.dtype or dtype in self.dtype_aliases:
            return self
        series_type = get_series_type_from_dtype(dtype)
        expression = series_type.from_dtype_to_sql(self.dtype, self.expression)
        # get the real dtype, in case the provided dtype was an alias. mypy needs some help
        new_dtype = cast(str, series_type.dtype)
        return self._get_derived_series(new_dtype=new_dtype, expression=expression)

    @classmethod
    def from_const(cls,
                   base: DataFrameOrSeries,
                   value: Any,
                   name: str) -> 'BuhTuhSeries':
        result = cls.get_class_instance(
            base=base,
            name=name,
            expression=Expression.construct_raw(cls.value_to_sql(value))
        )
        return result

    def equals(self, other: Any) -> bool:
        """
        Checks whether other is the same as self. This implements the check that would normally be
        implemented in __eq__, but we already use that method for other purposes.
        This strictly checks that other is the same type as self. If other is a subclass this will return
        False.
        """
        if not isinstance(other, self.__class__) or not isinstance(self, other.__class__):
            return False
        if (self.index is None) != (other.index is None):
            return False
        if self.index is not None and other.index is not None:
            if list(self.index.keys()) != list(other.index.keys()):
                return False
            for key in self.index.keys():
                if not self.index[key].equals(other.index[key]):
                    return False
        return self.engine == other.engine and \
            self.base_node == other.base_node and \
            self.name == other.name and \
            self.expression == other.expression and \
            self._sorted_ascending == other._sorted_ascending

    # Below methods are not abstract, as they can be optionally be implemented by subclasses.
    def __add__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __sub__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __mul__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    # TODO, answer: What about __matmul__?

    def __truediv__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __floordiv__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __mod__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    # TODO, answer: What about __divmod__?

    def __pow__(self, other, modulo=None) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __lshift__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __rshift__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __and__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __xor__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def __or__(self, other) -> 'BuhTuhSeries':
        raise NotImplementedError()

    def _comparator_operator(self, other, comparator) -> 'BuhTuhSeriesBoolean':
        raise NotImplementedError()

    def __ne__(self, other) -> 'BuhTuhSeriesBoolean':  # type: ignore
        return self._comparator_operator(other, "<>")

    def __eq__(self, other) -> 'BuhTuhSeriesBoolean':  # type: ignore
        return self._comparator_operator(other, "=")

    def __lt__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<")

    def __le__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<=")

    def __ge__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, ">=")

    def __gt__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, ">")

    def __getitem__(self, key: Union[Any, slice]):
        if isinstance(key, slice):
            raise NotImplementedError("index slices currently not supported")

        # any other value we treat as a literal index lookup
        # multiindex not supported atm
        if self.index is None:
            raise Exception('Function not supported on Series without index')
        if len(self.index) != 1:
            raise NotImplementedError('Index only implemented for simple indexes.')
        series = self.to_frame()[list(self.index.values())[0] == key]
        assert isinstance(series, self.__class__)

        # this is massively ugly
        return series.head(1).values[0]

    def _window_or_agg_func(
            self,
            partition: Optional['BuhTuhGroupBy'],
            expression: Expression,
            derived_dtype: str) -> 'BuhTuhSeries':

        from buhtuh.partitioning import BuhTuhWindow

        if partition is None or not isinstance(partition, BuhTuhWindow):
            return self._get_derived_series(derived_dtype, expression)
        else:
            return self._get_derived_series(derived_dtype, partition.get_window_expression(expression))

    # Maybe the aggregation methods should be defined on a more subclass of the actual Series call
    # so we can be more restrictive in calling these.
    def min(self, partition: 'BuhTuhGroupBy' = None):
        return self._window_or_agg_func(partition,
                                        Expression.construct('min({})', self.expression),
                                        self.dtype)

    def max(self, partition: 'BuhTuhGroupBy' = None):
        return self._window_or_agg_func(partition,
                                        Expression.construct('max({})', self.expression),
                                        self.dtype)

    def count(self, partition: 'BuhTuhGroupBy' = None):
        return self._window_or_agg_func(partition,
                                        Expression.construct('count({})', self.expression),
                                        'int64')

    def nunique(self, partition: 'BuhTuhGroupBy' = None):
        if partition is not None and isinstance(partition, BuhTuhWindow):
            raise Exception("unique counts in window functions not supported (by PG at least)")

        return self._get_derived_series('int64', Expression.construct('count(distinct {})', self.expression))

    # Window functions applicable for all types of data, but only with a window
    # TODO more specific docs
    # TODO make group_by optional, but for that we need some way to access the series' underlying
    #      df to access sorting

    def _check_window(self, partition: Any):
        """
        Validate that the given partition is a true BuhTuhWindow or raise an exception
        """
        from buhtuh.partitioning import BuhTuhWindow
        if not isinstance(partition, BuhTuhWindow):
            raise ValueError("Window functions need a BuhTuhWindow")

    def window_row_number(self, window: 'BuhTuhWindow'):
        """
        Returns the number of the current row within its partition, counting from 1.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('row_number()'), 'int64')

    def window_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the rank of the current row, with gaps; that is, the row_number of the first row
        in its peer group.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('rank()'), 'int64')

    def window_dense_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the rank of the current row, without gaps; this function effectively counts peer
        groups.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('dense_rank()'), 'int64')

    def window_percent_rank(self, window: 'BuhTuhWindow'):
        """
        Returns the relative rank of the current row, that is
            (rank - 1) / (total partition rows - 1).
        The value thus ranges from 0 to 1 inclusive.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('percent_rank()'), "double precision")

    def window_cume_dist(self, window: 'BuhTuhWindow'):
        """
        Returns the cumulative distribution, that is
            (number of partition rows preceding or peers with current row) / (total partition rows).
        The value thus ranges from 1/N to 1.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct('cume_dist()'), "double precision")

    def window_ntile(self, window: 'BuhTuhWindow', num_buckets: int = 1):
        """
        Returns an integer ranging from 1 to the argument value,
        dividing the partition as equally as possible.
        """
        self._check_window(window)
        return self._window_or_agg_func(window, Expression.construct(f'ntile({num_buckets})'), "int64")

    def window_lag(self, window: 'BuhTuhWindow', offset: int = 1, default: Any = None):
        """
        Returns value evaluated at the row that is offset rows before the current row
        within the partition; if there is no such row, instead returns default
        (which must be of the same type as value).

        Both offset and default are evaluated with respect to the current row.
        If omitted, offset defaults to 1 and default to None
        """
        self._check_window(window)
        default_sql = self.value_to_sql(default)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'lag({{}}, {offset}, {default_sql})', self.expression),
            self.dtype
        )

    def window_lead(self, window: 'BuhTuhWindow', offset: int = 1, default: Any = None):
        """
        Returns value evaluated at the row that is offset rows after the current row within the partition;
        if there is no such row, instead returns default (which must be of the same type as value).
        Both offset and default are evaluated with respect to the current row.
        If omitted, offset defaults to 1 and default to None.
        """
        self._check_window(window)
        default_sql = self.value_to_sql(default)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'lead({{}}, {offset}, {default_sql})', self.expression),
            self.dtype
        )

    def window_first_value(self, window: 'BuhTuhWindow'):
        """
        Returns value evaluated at the row that is the first row of the window frame.
        """
        self._check_window(window)
        return self._window_or_agg_func(
            window,
            Expression.construct('first_value({})', self.expression),
            self.dtype
        )

    def window_last_value(self, window: 'BuhTuhWindow'):
        """
        Returns value evaluated at the row that is the last row of the window frame.
        """
        self._check_window(window)
        return self._window_or_agg_func(
            window,
            Expression.construct('last_value({})', self.expression),
            self.dtype
        )

    def window_nth_value(self, window: 'BuhTuhWindow', n: int):
        """
        Returns value evaluated at the row that is the n'th row of the window frame
        (counting from 1); returns NULL if there is no such row.
        """
        self._check_window(window)
        return self._window_or_agg_func(
            window,
            Expression.construct(f'nth_value({{}}, {n})', self.expression),
            self.dtype
        )


class BuhTuhSeriesBoolean(BuhTuhSeries, ABC):
    dtype = 'bool'
    dtype_aliases = ('boolean', '?', bool)
    supported_db_dtype = 'boolean'
    supported_value_types = (bool, )

    @classmethod
    def value_to_sql(cls, value: bool) -> str:
        if value is None:
            return 'NULL'
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be bool, actual type: {type(value)}')
        return str(value)

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'bool':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to bool')
        return Expression.construct('cast({} as bool)', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['bool'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)

    def _boolean_operator(self, other, operator: str) -> 'BuhTuhSeriesBoolean':
        # TODO maybe "other" should have a way to tell us it can be a bool?
        # TODO we're missing "NOT" here. https://www.postgresql.org/docs/13/functions-logical.html
        other = const_to_series(base=self, value=other)
        self._check_supported(f"boolean operator '{operator}'", ['bool', 'int64', 'float'], other)
        if other.dtype != 'bool':
            expression = Expression.construct(
                f'(({{}}) {operator} ({{}}::bool))', self.expression, other.expression
            )
        else:
            expression = Expression.construct(
                f'(({{}}) {operator} ({{}}))', self.expression, other.expression
            )
        return self._get_derived_series('bool', expression)

    def __and__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._boolean_operator(other, 'AND')

    def __or__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._boolean_operator(other, 'OR')


class BuhTuhSeriesAbstractNumeric(BuhTuhSeries, ABC):
    """
    Base class that defines shared logic between BuhTuhSeriesInt64 and BuhTuhSeriesFloat64
    """
    def __add__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['int64', 'float64'], other)
        expression = Expression.construct('({}) + ({})', self.expression, other.expression)
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def __sub__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['int64', 'float64'], other)
        expression = Expression.construct('({}) - ({})', self.expression, other.expression)
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['int64', 'float64'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)

    def __truediv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = Expression.construct('cast({} as float) / ({})', self.expression, other.expression)
        return self._get_derived_series('float64', expression)

    def __floordiv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = Expression.construct('cast({} as bigint) / ({})', self.expression, other.expression)
        return self._get_derived_series('int64', expression)

    def sum(self, partition: 'BuhTuhGroupBy' = None):
        # TODO: This cast here is rather nasty
        return self._window_or_agg_func(
            partition,
            Expression.construct('cast(sum({}) as bigint)', self.expression),
            'int64'
        )

    def average(self, partition: 'BuhTuhGroupBy' = None) -> 'BuhTuhSeriesFloat64':
        result = self._window_or_agg_func(
            partition,
            Expression.construct('avg({})', self.expression),
            'double precision'
        )
        return cast('BuhTuhSeriesFloat64', result)


class BuhTuhSeriesInt64(BuhTuhSeriesAbstractNumeric):
    dtype = 'int64'
    dtype_aliases = ('integer', 'bigint', 'i8', int, numpy.int64)
    supported_db_dtype = 'bigint'
    supported_value_types = (int, numpy.int64)

    @classmethod
    def value_to_sql(cls, value: int) -> str:
        # TODO validate this, should be part of Nullable logic?
        if value is None:
            return 'NULL'
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be int, actual type: {type(value)}')
        return f'{value}::bigint'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'int64':
            return expression
        if source_dtype not in ['float64', 'bool', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to int64')
        return Expression.construct('cast({} as bigint)', expression)


class BuhTuhSeriesFloat64(BuhTuhSeriesAbstractNumeric):
    dtype = 'float64'
    dtype_aliases = ('float', 'double', 'f8', float, numpy.float64, 'double precision')
    supported_db_dtype = 'double precision'
    supported_value_types = (float, numpy.float64)

    @classmethod
    def value_to_sql(cls, value: Union[float, numpy.float64]) -> str:
        if value is None:
            return 'NULL'
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be float, actual type: {type(value)}')
        return f'{value}::float'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'float64':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to float64')
        return Expression.construct('cast({} as float)', expression)


class BuhTuhSeriesString(BuhTuhSeries):
    dtype = 'string'
    dtype_aliases = ('text', str)
    supported_db_dtype = 'text'
    supported_value_types = (str, )

    @classmethod
    def value_to_sql(cls, value: str) -> str:
        if value is None:
            return 'NULL'
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be str, actual type: {type(value)}')
        # TODO: fix sql injection!
        return f"'{value}'"

    @classmethod
    def from_dtype_to_sql(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'string':
            return expression
        return Expression.construct('cast(({}) as text)', expression)

    def __add__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['string'], other)
        expression = Expression.construct('({}) || ({})', self.expression, other.expression)
        return self._get_derived_series('string', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['string'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)

    def slice(self, start: Union[int, slice], stop: int = None) -> 'BuhTuhSeriesString':
        """
        Get a python string slice using DB functions. Format follows standard slice format
        Note: this is called 'slice' to not destroy index selection logic
        :param item: an int for a single character, or a slice for some nice slicing
        :return: BuhTuhSeriesString with the slice applied
        """
        if isinstance(start, (int, type(None))):
            item = slice(start, stop)
        elif isinstance(start, slice):
            item = start
        else:
            raise ValueError(f'Type not supported {type(start)}')

        expression = self.expression

        if item.start is not None and item.start < 0:
            expression = Expression.construct(f'right({{}}, {abs(item.start)})', expression)
            if item.stop is not None:
                if item.stop < 0 and item.stop > item.start:
                    # we needed to check stop < 0, because that would mean we're going the wrong direction
                    # and that's not supported
                    expression = Expression.construct(f'left({{}}, {item.stop - item.start})', expression)
                else:
                    expression = Expression.construct("''")

        elif item.stop is not None and item.stop < 0:
            # we need to get the full string, minus abs(stop) chars.
            expression = Expression.construct(
                f'substr({{}}, 1, greatest(0, length({{}}){item.stop}))',
                expression, expression
            )

        else:
            # positives only
            if item.stop is None:
                if item.start is None:
                    # full string, what are we doing here?
                    # current expression is okay.
                    pass
                else:
                    # full string starting at start
                    expression = Expression.construct(f'substr({{}}, {item.start+1})', expression)
            else:
                if item.start is None:
                    expression = Expression.construct(f'left({{}}, {item.stop})', expression)
                else:
                    if item.stop > item.start:
                        expression = Expression.construct(
                            f'substr({{}}, {item.start+1}, {item.stop-item.start})',
                            expression
                        )
                    else:
                        expression = Expression.construct("''")

        return self._get_derived_series('string', expression)


class BuhTuhSeriesUuid(BuhTuhSeries):
    """
    Series representing UUID values.
    """
    dtype = 'uuid'
    dtype_aliases = ()
    supported_db_dtype = 'uuid'
    supported_value_types = (UUID, )

    @classmethod
    def value_to_sql(cls, value: UUID) -> str:
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be uuid, actual type: {type(value)}')
        return f"cast('{value}' as uuid)"

    @classmethod
    def from_dtype_to_sql(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'uuid':
            return expression
        if source_dtype == 'string':
            # If the format is wrong, then this will give an error later on, but there is not much we can
            # do about that here.
            return Expression.construct('cast(({}) as uuid)', expression)
        # As far as we know the other types we support cannot be directly cast to uuid.
        raise ValueError(f'cannot convert {source_dtype} to uuid.')

    @classmethod
    def sql_gen_random_uuid(cls, base: DataFrameOrSeries) -> 'BuhTuhSeriesUuid':
        """
        Create a new Series object with for every row the `gen_random_uuid()` expression, which will
        evaluate to a random uuid for each row.

        Note that this is non-deterministic expression, it will give a different result each time it is run.
        This can have some unexpected consequences. Considers the following code:
            df['x'] = BuhTuhSeriesUuid.sql_gen_random_uuid(df)
            df['y'] = df['x']
            df['different'] = df['y'] != df['x']
        The df['different'] column will be True for all rows, because the second statement copies the
        unevaluated expression, not the result of the expression. So at evaluation time the expression will
        be evaluated twice for each row, for the 'x' column and the 'y' column, giving different results both
        times. One way to work around this is to materialize the dataframe in its current state (using
        get_df_materialized_model()), before adding any columns that reference a column that's created with
        this function.
        """
        return cls.get_class_instance(
            base=base,
            name='__tmp',
            expression=Expression.construct('gen_random_uuid()')
        )

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['uuid'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('uuid', expression)


class BuhTuhSeriesJson(BuhTuhSeries):
    """
    TODO: make this a proper class, not just a string subclass
    """
    dtype = 'json'
    dtype_aliases = (object, )  # type: ignore
    supported_db_dtype = 'json'
    supported_value_types = (dict, list)

    def __init__(self,
                 engine,
                 base_node: SqlModel,
                 index: Optional[Dict[str, 'BuhTuhSeries']],
                 name: str,
                 expression: Expression = None,
                 sorted_ascending: Optional[bool] = None):
        super().__init__(engine,
                         base_node,
                         index,
                         name,
                         expression,
                         sorted_ascending)
        self.json = Json(self)

    @classmethod
    def value_to_sql(cls, value: dict) -> str:
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be dict, actual type: {type(value)}')
        json_value = json.dumps(value)
        escaped_json_value = json_value.replace("'", "''")
        return f"cast('{escaped_json_value}' to json)"

    @classmethod
    def from_dtype_to_sql(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'json':
            return expression
        if source_dtype != 'string':
            raise ValueError(f'cannot convert {source_dtype} to json')
        return Expression.construct('cast({} as json)', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['json'], other)
        expression = Expression.construct(
            f'({{}})::jsonb {comparator} ({{}})::jsonb',
            self.expression, other.expression
        )
        return self._get_derived_series('bool', expression)

    def __le__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<@")


class BuhTuhSeriesTimestamp(BuhTuhSeries):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        timestamp without time zone
    """
    dtype = 'timestamp'
    dtype_aliases = ('datetime64', 'datetime64[ns]', numpy.datetime64)
    supported_db_dtype = 'timestamp without time zone'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.datetime]) -> str:
        if value is None:
            return 'NULL'
        if isinstance(value, datetime.date):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.datetime, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTimestamp.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timestamp':
            return expression
        else:
            if source_dtype not in ['string', 'date']:
                raise ValueError(f'cannot convert {source_dtype} to timestamp')
            return Expression.construct(f'({{}}::{BuhTuhSeriesTimestamp.supported_db_dtype})', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timestamp', 'date', 'string'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/14/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = Expression.construct(f"to_char({{}}, '{format}')", self.expression)
        return self._get_derived_series('string', expr)

    def __sub__(self, other) -> 'BuhTuhSeriesTimestamp':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timestamp', 'date', 'time'], other)
        expression = Expression.construct('({}) - ({})', self.expression, other.expression)
        return self._get_derived_series('timedelta', expression)


class BuhTuhSeriesDate(BuhTuhSeriesTimestamp):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        date
    """
    dtype = 'date'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'date'
    supported_value_types = (datetime.datetime, datetime.date, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.date]) -> str:
        if value is None:
            return 'NULL'
        if isinstance(value, datetime.date):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.date, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesDate.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'date':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to date')
            return Expression.construct(f'({{}}::{BuhTuhSeriesDate.supported_db_dtype})', expression)


class BuhTuhSeriesTime(BuhTuhSeries):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        time without time zone
    """
    dtype = 'time'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'time without time zone'
    supported_value_types = (datetime.time, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, datetime.time]) -> str:
        if value is None:
            return 'NULL'
        if isinstance(value, datetime.time):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or datetime.time, actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTime.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'time':
            return expression
        else:
            if source_dtype not in ['string', 'timestamp']:
                raise ValueError(f'cannot convert {source_dtype} to time')
            return Expression.construct('({{}}::{BuhTuhSeriesTime.supported_db_dtype})', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['time', 'string'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)


class BuhTuhSeriesTimedelta(BuhTuhSeries):
    dtype = 'timedelta'
    dtype_aliases = ('interval',)
    supported_db_dtype = 'interval'
    supported_value_types = (datetime.timedelta, numpy.timedelta64, str)

    @classmethod
    def value_to_sql(cls, value: Union[str, numpy.timedelta64, datetime.timedelta]) -> str:
        if value is None:
            return 'NULL'
        if isinstance(value, (numpy.timedelta64, datetime.timedelta)):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or (numpy.timedelta64, datetime.timedelta), '
                            f'actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'::{BuhTuhSeriesTimedelta.supported_db_dtype}"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'timedelta':
            return expression
        else:
            if not source_dtype == 'string':
                raise ValueError(f'cannot convert {source_dtype} to timedelta')
            return Expression.construct('cast({} as interval)', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timedelta', 'date', 'time', 'string'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self.expression, other.expression)
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/9.1/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = Expression.construct(f"to_char({{}}, '{format}')", self.expression)
        return self._get_derived_series('string', expr)

    def __add__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = Expression.construct('({}) + ({})', self.expression, other.expression)
        return self._get_derived_series('timedelta', expression)

    def __sub__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = Expression.construct('({}) - ({})', self.expression, other.expression)
        return self._get_derived_series('timedelta', expression)

    def sum(self, partition: 'BuhTuhGroupBy' = None) -> 'BuhTuhSeriesTimedelta':
        result = self._window_or_agg_func(
            partition,
            Expression.construct('sum({})', self.expression),
            'timedelta'
        )
        return cast('BuhTuhSeriesTimedelta', result)

    def average(self, partition: 'BuhTuhGroupBy' = None) -> 'BuhTuhSeriesTimedelta':
        result = self._window_or_agg_func(
            partition,
            Expression.construct('avg({})', self.expression),
            'timedelta'
        )
        return cast('BuhTuhSeriesTimedelta', result)


def const_to_series(base: Union[BuhTuhSeries, BuhTuhDataFrame],
                    value: Union[BuhTuhSeries, int, float, str, UUID],
                    name: str = None) -> BuhTuhSeries:
    """
    Take a value and return a BuhTuhSeries representing a column with that value.
    If value is already a BuhTuhSeries it is returned unchanged.
    If value is a constant then the right BuhTuhSeries subclass is found for that type and instantiated
    with the constant value.
    :param base: Base series or DataFrame. In case a new Series object is created and returned, it will
        share its engine, index, and base_node with this one. Only applies if value is not a BuhTuhSeries
    :param value: constant value for which to create a Series, or a BuhTuhSeries
    :param name: optional name for the series object. Only applies if value is not a BuhTuhSeries
    :return:
    """
    if isinstance(value, BuhTuhSeries):
        return value
    name = '__tmp' if name is None else name
    dtype = value_to_dtype(value)
    series_type = get_series_type_from_dtype(dtype)
    return series_type.from_const(base=base, value=value, name=name)
