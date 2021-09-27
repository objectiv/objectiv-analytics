import datetime
from abc import abstractmethod, ABC
from copy import copy
from typing import List, Set, Union, Dict, Any, Optional, Tuple, cast

import numpy
import pandas
import pandas as pd
from sqlalchemy.engine import Engine

from sql_models.model import SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql
from buhtuh.types import get_series_type_from_dtype, arg_to_type


DataFrameOrSeries = Union['BuhTuhDataFrame', 'BuhTuhSeries']
ColumnNames = Union[str, List[str]]


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

    The initial data of the DataFrame is the result of the SQL query that the `source_node` parameter
    contains. That can be a simple query on a table, but also a complicated query in itself. Operations
    on the data will result in SQL queries that build on top of the query of the source_node. The
    index and series parameters contain meta information about the data in the source_node.

    The API of this DataFrame is partially compatible with Pandas DataFrames. For more on Pandas
    DataFrames see https://pandas.pydata.org/docs/reference/frame.html
    """
    def __init__(
        self,
        engine: Engine,
        source_node: SqlModel,
        index: Dict[str, 'BuhTuhSeries'],
        series: Dict[str, 'BuhTuhSeries']
    ):
        """
        Instantiate a new BuhTuhDataFrame.
        There are utility class methods to easily create a BuhTuhDataFrame from existing data such as a
        table (`from_table()`) or already instantiated sql-model (`from_model()`).

        :param engine: db connection
        :param source_node: sql-model of a select statement that must contain all columns/expressions that
            are present in the series parameter.
        :param index: Dictionary mapping the name of each index-column to a Series object representing
            the column.
        :param series: Dictionary mapping the name of each data-column to a Series object representing
            the column.
        """
        self._engine = engine
        self._base_node = source_node
        self._index = copy(index)
        self._data: Dict[str, BuhTuhSeries] = {}
        for key, value in series.items():
            if key != value.name:
                raise ValueError(f'Keys in `series` should match the name of series. '
                                 f'key: {key}, series.name: {value.name}')
            self._data[key] = value
        if set(index.keys()) & set(series.keys()):
            raise ValueError(f"The names of the index series and data series should not intersect. "
                             f"Index series: {sorted(index.keys())} data series: {sorted(series.keys())}")

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

    @classmethod
    def _get_dtypes(cls, engine, node):
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
        return {x[0]: x[1] for x in res.fetchall()}

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
            source_node=model,
            index_dtypes=index_dtypes,
            dtypes=series_dtypes
        )

    @classmethod
    def from_dataframe(cls, df: pandas.DataFrame, name: str, engine: Engine, if_exists: str = 'fail'):
        """
        Instantiate a new BuhTuhDataFrame based on the content of a Pandas DataFrame. This will first load
        the data into the database using pandas' df.to_sql() method.
        """

        if df.index.name is None:  # for now only one index allowed
            index = '_index_0'
        else:
            index = f'_index_{df.index.name}'
        conn = engine.connect()
        df.to_sql(name=name, con=conn, if_exists=if_exists, index_label=index)
        conn.close()

        # Todo, this should use from_table from here on.
        model = CustomSqlModel(sql=f'SELECT * FROM {name}').instantiate()

        dtypes = {column_name: dtype.name for column_name, dtype in df.dtypes.items()}
        # Should this also use _df_or_series?
        return cls.get_instance(
            engine=engine,
            source_node=model,
            index_dtypes={index: df.index.dtype.name},
            dtypes=dtypes
        )

    @classmethod
    def get_instance(
            cls,
            engine,
            source_node: SqlModel,
            index_dtypes: Dict[str, str],
            dtypes: Dict[str, str]
    ) -> 'BuhTuhDataFrame':
        """
        Get an instance with the right series instantiated based on the dtypes array. This assumes that
        source_node has a column for all names in index_dtypes and dtypes.
        """

        index: Dict[str, BuhTuhSeries] = {}
        for key, value in index_dtypes.items():
            index_type = get_series_type_from_dtype(value)
            index[key] = index_type(
                engine=engine,
                base_node=source_node,
                index=None,  # No index for index
                name=key
            )
        series: Dict[str, BuhTuhSeries] = {}
        for key, value in dtypes.items():
            series_type = get_series_type_from_dtype(value)
            series[key] = series_type(
                engine=engine,
                base_node=source_node,
                index=index,
                name=key
            )
        return BuhTuhDataFrame(
            engine=engine,
            source_node=source_node,
            index=index,
            series=series
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

    def __getitem__(self, key: Union[str, List[str], Set[str], 'BuhTuhSeriesBoolean']) -> DataFrameOrSeries:
        """
        TODO: Comments
        :param key:
        :return:
        """

        if isinstance(key, str):
            return self.data[key]
        if isinstance(key, (set, list)):
            key_set = set(key)
            selected_data = {key: data for key, data in self.data.items() if key in key_set}

            return BuhTuhDataFrame(
                    engine=self.engine,
                    source_node=self.base_node,
                    index=self.index,
                    series=selected_data
                )

        if isinstance(key, slice):
            model = self.get_current_node(limit=key)
            return self._df_or_series(
                df=BuhTuhDataFrame(
                    engine=self.engine,
                    source_node=model,
                    index=self.index,
                    series=self.data
                )
            )

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
                    source_node=model,
                    index_dtypes={name: series.dtype for name, series in self.index.items()},
                    dtypes={name: series.dtype for name, series in self.data.items()}
                )
            )
        raise NotImplementedError(f"Only str, (set|list)[str], slice or BuhTuhSeriesBoolean are supported, "
                                  f"but got {type(key)}")

    def __getattr__(self, attr):
        return self._data[attr]

    def __setitem__(self,
                    key: Union[str, List[str]],
                    value: Union['BuhTuhSeries', int, str, float]):
        """
        TODO: Comments
        """
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
        if isinstance(dtype, str):
            dtype = {column: dtype for column in self.data_columns}
        if not isinstance(dtype, dict) or not all(isinstance(column, str) for column in dtype.values()):
            raise ValueError(f'dtype should either be a string or a dictionary mapping to strings.')
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

        return BuhTuhDataFrame(
            engine=self.engine,
            source_node=self.base_node,
            index=self.index,
            series=new_data
        )

    def groupby(
            self,
            by: Union[str, 'BuhTuhSeries', List[str], List['BuhTuhSeries']] = None
    ) -> 'BuhTuhGroupBy':
        """
        Group by any of the series currently in this dataframe, both from index
        as well as data.
        :param by: The series to group by
        :return: an object to perform aggregations on
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

        # TODO We used to create a new instance of this df before passing it on. Did that have value?

        return BuhTuhGroupBy(buh_tuh=self, group_by_columns=group_by_columns)

    def sort_values(
            self,
            by: Union[str, List[str]],
            ascending: Union[bool, List[bool]] = True
    ) -> 'BuhTuhDataFrame':
        """
        Create a new DataFrame with the specified sorting order.

        This does not modify the current DataFrame, instead it returns a new DataFrame.

        :param by: column label or list of labels to sort by.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            by must also be a list and len(ascending) == len(by)
        :return: a new DataFrame with the specified ordering
        """
        # TODO needs type check?
        if isinstance(by, str):
            by = [by]
        if isinstance(ascending, bool):
            ascending = [ascending] * len(by)
        if len(by) != len(ascending):
            raise ValueError(f'Length of ascending ({len(ascending)}) != length of by ({len(by)})')
        sort_order = dict(zip(by, ascending))
        possible_names = list(self.index.keys()) + list(self.data.keys())
        missing = [name for name in sort_order.keys() if name not in possible_names]
        if len(missing) > 0:
            raise ValueError(f'Some series could not be found in current frame: {missing}')

        model = self.get_current_node(order=sort_order)
        return BuhTuhDataFrame.get_instance(
            engine=self.engine,
            source_node=model,
            index_dtypes={name: series.dtype for name, series in self.index.items()},
            dtypes={name: series.dtype for name, series in self.data.items()}
        )

    def to_df(self) -> pandas.DataFrame:
        """
        Run a SQL query representing the current state of this DataFrame against the database and return the
        resulting data as a Pandas DataFrame.

        This function queries the database.
        """
        conn = self.engine.connect()
        sql = self.view_sql()
        df = pd.read_sql_query(sql, conn, index_col=list(self.index.keys()))
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
        df = pd.read_sql_query(sql, conn, index_col=list(self.index.keys()))
        conn.close()
        return df

    def get_current_node(
            self,
            limit: Union[int, slice] = None, order: Dict[str, bool] = None
    ) -> SqlModel[CustomSqlModel]:
        """
        Translate the current state of this DataFrame into a SqlModel.
        :param limit: The limit to use
        :param order: The data series to order by, where the bool specifies ASC or DESC.
                      If missing will use index ASC otherwise)
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

        if order:
            order_str = ", ".join(f"{name} {'asc' if asc else 'desc'}" for name, asc in order.items())
            order_str = f'order by {order_str}'
        else:
            order_str = ''

        model_builder = CustomSqlModel(
            name='view_sql',
            sql='select {index_str}, {columns_sql_str} from {{_last_node}} {order} {limit}'
        )

        return model_builder(
            columns_sql_str=self._get_all_column_expressions(),
            index_str=', '.join(self.index.keys()),
            _last_node=self.base_node,
            limit='' if limit_str is None else f'{limit_str}',
            order=order_str
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
        Join the right Dataframe or Series on self.. This will return a new DataFrame that contains the
        combined columns of both dataframes, and the rows that result from joining on the specified columns.
        The columns that are joined on can consists (partially or fully) out of index columns.

        See buhtuh.merge.merge() for more information.
        The interface of this function is similar to pandas' merge, but the following parameters are not
        supported: sort, copy, indicator, and validate.
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
                 expression: str = None):
        """
        TODO: docstring
        :param engine:
        :param base_node:
        :param index: None if this Series is part of an index. Otherwise a dict with the Series that are
                        this Series' index
        :param name:
        :param expression:
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
            self._expression = f'{{table_alias}}"{self.name}"'

    @property
    @abstractmethod
    def dtype(self) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def constant_to_sql(value: Any) -> str:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
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
    def expression(self) -> str:
        return self._expression

    def head(self, n: int = 5):
        """
        Return the first `n` rows.
        """
        # TODO get a series directly instead of ripping it out of the df?
        return self.to_frame().head(n)[self.name]

    def sort_values(self, sort_order):
        # TODO sort series directly instead of ripping it out of the df?
        return self.to_frame().sort_values(sort_order)[self.name]

    def view_sql(self):
        return self.to_frame().view_sql()

    def to_frame(self) -> BuhTuhDataFrame:
        if self.index is None:
            raise Exception('to_frame() is not supported for Series that do not have an index')
        return BuhTuhDataFrame(
            engine=self.engine,
            source_node=self.base_node,
            index=self.index,
            series={self.name: self}
        )

    @classmethod
    def get_instance(
            cls,
            base: DataFrameOrSeries,
            name: str,
            dtype: str,
            expression: str = None
    ) -> 'BuhTuhSeries':
        """
        Create an instance of the right sub-class of BuhTuhSeries.
        The subclass is based on the provided dtype. See docstring of __init__ for other parameters.
        """
        series_type = get_series_type_from_dtype(dtype=dtype)
        return series_type(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=expression
        )

    def get_expression(self, table_alias='') -> str:
        # TODO BLOCKER! escape the stuff

        if table_alias != '' and table_alias[-1] != '.':
            table_alias = table_alias + '.'

        return self.expression.format(table_alias=table_alias)

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
            raise ValueError(f'{operation_name} not supported between {self.dtype} and {other.dtype}.')

    def _get_derived_series(self, new_dtype: str, expression: str):
        return BuhTuhSeries.get_instance(
            base=self,
            name=self.name,
            dtype=new_dtype,
            expression=expression
        )

    def astype(self, dtype: str) -> 'BuhTuhSeries':
        if dtype == self.dtype:
            return self
        series_type = get_series_type_from_dtype(dtype)
        expression = series_type.from_dtype_to_sql(self.dtype, self.get_expression())
        return self._get_derived_series(new_dtype=dtype, expression=expression)

    @classmethod
    def from_const(cls,
                   base: DataFrameOrSeries,
                   value: Any,
                   name: str) -> 'BuhTuhSeries':
        dtype = cast(str, cls.dtype)  # needed for mypy
        result = BuhTuhSeries.get_instance(
            base=base,
            name=name,
            dtype=dtype,
            expression=cls.constant_to_sql(value)
        )
        return result

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

    # Maybe the aggregation methods should be defined on a more subclass of the actual Series call
    # so we can be more restrictive in calling these.
    def min(self):
        return self._get_derived_series(self.dtype, f'min({self.expression})')

    def max(self):
        return self._get_derived_series(self.dtype, f'max({self.expression})')

    def count(self):
        return self._get_derived_series('int64', f'count({self.expression})')

    def nunique(self):
        return self._get_derived_series('int64', f'count(distinct {self.expression})')


class BuhTuhSeriesBoolean(BuhTuhSeries, ABC):
    dtype = "bool"

    @staticmethod
    def constant_to_sql(value: bool) -> str:
        if not isinstance(value, bool):
            raise TypeError(f'value should be bool, actual type: {type(value)}')
        return str(value)

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'bool':
            return expression
        else:
            return f'({expression})::bool'

    def _boolean_operator(self, other, operator) -> 'BuhTuhSeriesBoolean':
        # TODO maybe "other" should have a way to tell us it can be a bool?
        # TODO we're missing "NOT" here. https://www.postgresql.org/docs/13/functions-logical.html
        other = const_to_series(base=self, value=other)
        self._check_supported(f"boolean operator '{operator}'", ['bool', 'int64', 'float'], other)
        if other.dtype != 'bool':
            expression = f'(({self.expression}) {operator} ({other.expression}::bool))'
        else:
            expression = f'(({self.expression}) {operator} ({other.expression}))'
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
        expression = f'({self.expression}) + ({other.expression})'
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def __sub__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['int64', 'float64'], other)
        expression = f'({self.expression}) - ({other.expression})'
        new_dtype = 'float64' if 'float64' in (self.dtype, other.dtype) else 'int64'
        return self._get_derived_series(new_dtype, expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['int64', 'float64'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def __truediv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = f'({self.expression})::float / ({other.expression})'
        return self._get_derived_series('float64', expression)

    def __floordiv__(self, other):
        other = const_to_series(base=self, value=other)
        self._check_supported('division', ['int64', 'float64'], other)
        expression = f'({self.expression})::int / ({other.expression})::int'
        return self._get_derived_series('int64', expression)

    def sum(self):
        # TODO: This cast here is rather nasty
        return self._get_derived_series('int64', f'sum({self.expression})::int')


class BuhTuhSeriesInt64(BuhTuhSeriesAbstractNumeric):
    dtype = 'Int64'

    @staticmethod
    def constant_to_sql(value: int) -> str:
        if not isinstance(value, (int, numpy.int64)):
            raise TypeError(f'value should be int, actual type: {type(value)}')
        return str(value)

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'Int64':
            return expression
        else:
            return f'({expression})::int'


class BuhTuhSeriesFloat64(BuhTuhSeriesAbstractNumeric):
    dtype = 'Float64'

    @staticmethod
    def constant_to_sql(value: float) -> str:
        if not isinstance(value, float):
            raise TypeError(f'value should be float, actual type: {type(value)}')
        return f'{value}::float'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'Float64':
            return expression
        else:
            return f'({expression})::float'


class BuhTuhSeriesString(BuhTuhSeries):
    dtype = 'string'

    @staticmethod
    def constant_to_sql(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f'value should be str, actual type: {type(value)}')
        # TODO: fix sql injection!
        return f"'{value}'"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'String':
            return expression
        else:
            return f'({expression})::varchar'

    def __add__(self, other) -> 'BuhTuhSeries':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['string'], other)
        expression = f'({self.expression}) || ({other.expression})'
        return self._get_derived_series('string', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
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
            expression = f'right({expression}, {abs(item.start)})'
            if item.stop is not None:
                if item.stop < 0 and item.stop > item.start:
                    # we needed to check stop < 0, because that would mean we're going the wrong direction
                    # and that's not supported
                    expression = f'left({expression}, {item.stop - item.start})'
                else:
                    expression = "''"

        elif item.stop is not None and item.stop < 0:
            # we need to get the full string, minus abs(stop) chars.
            expression = f'substr({expression}, 1, greatest(0, length({expression}){item.stop}))'

        else:
            # positives only
            if item.stop is None:
                if item.start is None:
                    # full string, what are we doing here?
                    # current expression is okay.
                    pass
                else:
                    # full string starting at start
                    expression = f'substr({expression}, {item.start+1})'
            else:
                if item.start is None:
                    expression = f'left({expression}, {item.stop})'
                else:
                    if item.stop > item.start:
                        expression = f'substr({expression}, {item.start+1}, {item.stop-item.start})'
                    else:
                        expression = "''"

        return self._get_derived_series('string', expression)


class BuhTuhSeriesTimestamp(BuhTuhSeries):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        timestamp without time zone
    """
    dtype = 'timestamp'

    db_dtype = 'timezone without time zone'

    @staticmethod
    def constant_to_sql(value: Union[str, datetime.datetime]) -> str:
        # This is wrong. We need a timedelta datatype
        if isinstance(value, (datetime.datetime, datetime.date, numpy.timedelta64)):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or (datetime.datetime, datetime.date, numpy.timedelta64)'
                            f', actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'timestamp':
            return expression
        else:
            return f'({expression}::{BuhTuhSeriesTimestamp.db_dtype})'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timestamp', 'date', 'time', 'string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/9.1/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = f"to_char({self.expression}, '{format}')"
        return self._get_derived_series('string', expr)

    def __sub__(self, other) -> 'BuhTuhSeriesTimestamp':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) - ({other.expression})'
        return self._get_derived_series('timedelta', expression)


class BuhTuhSeriesDate(BuhTuhSeriesTimestamp):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        date
    """
    dtype = 'date'
    db_dtype = 'date'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'date':
            return expression
        else:
            return f'({expression}::{BuhTuhSeriesDate.db_dtype})'


class BuhTuhSeriesTime(BuhTuhSeriesTimestamp):
    """
    Types in PG that we want to support: https://www.postgresql.org/docs/9.1/datatype-datetime.html
        time without time zone
    """
    dtype = 'time'
    db_dtype = 'time without time zone'

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'time':
            return expression
        else:
            return f'({expression}::{BuhTuhSeriesTime.db_dtype})'


class BuhTuhSeriesTimedelta(BuhTuhSeries):
    dtype = 'timedelta'
    db_dtype = 'interval'

    @staticmethod
    def constant_to_sql(value: Union[str, datetime.datetime]) -> str:
        if isinstance(value, (numpy.timedelta64, datetime.timedelta)):
            value = str(value)
        if not isinstance(value, str):
            raise TypeError(f'value should be str or (datetime.datetime, datetime.date, numpy.timedelta64)'
                            f', actual type: {type(value)}')
        # TODO: fix sql injection!
        # Maybe we should do some checking on syntax here?
        return f"'{value}'"

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'timedelta':
            return expression
        else:
            return f'({expression}::{BuhTuhSeriesTimedelta.db_dtype})'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['timedelta', 'date', 'time', 'string'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

    def format(self, format) -> 'BuhTuhSeriesString':
        """
        Allow standard PG formatting of this Series (to a string type)

        :param format: The format as defined in https://www.postgresql.org/docs/9.1/functions-formatting.html
        :return: a derived Series that accepts and returns formatted timestamp strings
        """
        expr = f"to_char({self.expression}, '{format}')"
        return self._get_derived_series('string', expr)

    def __add__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('add', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) + ({other.expression})'
        return self._get_derived_series('timedelta', expression)

    def __sub__(self, other) -> 'BuhTuhSeriesTimedelta':
        other = const_to_series(base=self, value=other)
        self._check_supported('sub', ['timedelta', 'timestamp', 'date', 'time'], other)
        expression = f'({self.expression}) - ({other.expression})'
        return self._get_derived_series('timedelta', expression)

    def sum(self) -> 'BuhTuhSeriesTimedelta':
        return self._get_derived_series('timedelta', f'sum({self.expression})')

    def average(self) -> 'BuhTuhSeriesTimedelta':
        return self._get_derived_series('timedelta', f'avg({self.expression})')


class BuhTuhGroupBy:
    def __init__(self,
                 buh_tuh: BuhTuhDataFrame,
                 group_by_columns: List['BuhTuhSeries']):
        self.buh_tuh = buh_tuh

        self.groupby = {}
        for col in group_by_columns:
            if not isinstance(col, BuhTuhSeries):
                raise ValueError(f'Unsupported groupby argument type: {type(col)}')
            assert col.base_node == buh_tuh.base_node
            self.groupby[col.name] = col

        if len(group_by_columns) == 0:
            # create new dummy column so we can aggregate over everything
            self.groupby = {
                'index': BuhTuhSeriesInt64.get_instance(base=buh_tuh,
                                                        name='index',
                                                        dtype='int64',
                                                        expression='1')
            }

        self.aggregated_data = {name: series
                                for name, series in buh_tuh.all_series.items()
                                if name not in self.groupby.keys()}

    def aggregate(
            self,
            series: Union[Dict[str, str], List[str]],
            aggregations: List[str] = None
    ) -> BuhTuhDataFrame:
        """
        Execute requested aggregations on this groupby

        :param series: a dict containing 'name': 'aggregation_method'.
            In case you need duplicates: a list of 'name's is also supported, but aggregations should have
            the same length list with the aggregation methods requested
        :param aggregations: The aggregation methods requested in case series is a list.
        :return: a new BuhTuhDataFrame containing the requested aggregations
        """
        new_series_dtypes = {}
        aggregate_columns = []

        if isinstance(series, list):
            if not isinstance(aggregations, list):
                raise ValueError('aggregations must be a list if series is a list')
            if len(series) != len(aggregations):
                raise ValueError(f'Length of series should match length of aggregations: '
                                 f'{len(series)} != {len(aggregations)}')
        elif isinstance(series, dict):
            aggregations = list(series.values())
            series = list(series.keys())
        else:
            raise TypeError()

        for name, aggregation in list(zip(series, aggregations)):
            data_series = self.aggregated_data[name]
            func = getattr(data_series, aggregation)
            agg_series = func()
            name = f'{agg_series.name}_{aggregation}'
            agg_series = BuhTuhSeries.get_instance(base=self.buh_tuh,
                                                   name=name,
                                                   dtype=agg_series.dtype,
                                                   expression=agg_series.expression)
            aggregate_columns.append(agg_series.get_column_expression())
            new_series_dtypes[agg_series.name] = agg_series.dtype

        model_builder = CustomSqlModel(  # setting this stuff could also be part of __init__
            sql="""
                select {group_by_columns}, {aggregate_columns}

                from {{prev}}
                group by {group_by_expression}
                """
        )
        model = model_builder(
            group_by_columns=', '.join(g.get_column_expression() for g in self.groupby.values()),
            aggregate_columns=', '.join(aggregate_columns),
            group_by_expression=', '.join(g.get_expression() for g in self.groupby.values()),
            # TODO: get final node, or at least make sure we 'freeze' the node?
            prev=self.buh_tuh.base_node
        )

        return BuhTuhDataFrame.get_instance(
            engine=self.buh_tuh.engine,
            source_node=model,
            index_dtypes={n: t.dtype for n, t in self.groupby.items()},
            dtypes=new_series_dtypes
        )

    def __getattr__(self, attr_name: str) -> Any:
        """ All methods that do not exists yet are potential aggregation methods. """
        try:
            return super().__getattribute__(attr_name)
        except AttributeError:
            return lambda: self.aggregate({series_name: attr_name for series_name in self.aggregated_data})

    def __getitem__(self, key: Union[str, List[str]]) -> 'BuhTuhGroupBy':

        assert isinstance(key, (str, list, tuple)), f'a buhtuh `selection` should be a str or list but ' \
                                                    f'got {type(key)} instead.'

        if isinstance(key, str):
            key = [key]

        key_set = set(key)
        # todo: check that the key_set is not in group_by_data, or make sure we fix the duplicate column
        #  name problem?
        assert key_set.issubset(set(self.aggregated_data.keys()))

        selected_data = {key: data for key, data in self.aggregated_data.items() if key in key_set}
        buh_tuh = BuhTuhDataFrame(
            engine=self.buh_tuh.engine,
            source_node=self.buh_tuh.base_node,
            index=self.groupby,
            series=selected_data
        )
        return BuhTuhGroupBy(buh_tuh=buh_tuh, group_by_columns=list(self.groupby.values()))


def const_to_series(base: Union[BuhTuhSeries, BuhTuhDataFrame],
                    value: Union[BuhTuhSeries, int, float, str],
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
    dtype = arg_to_type(value)
    series_type = get_series_type_from_dtype(dtype)
    return series_type.from_const(base=base, value=value, name=name)
