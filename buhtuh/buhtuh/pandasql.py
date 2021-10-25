from copy import copy
from typing import List, Set, Union, Dict, Any, Optional, Tuple, cast, NamedTuple, \
    TYPE_CHECKING, Callable, Sequence
from uuid import UUID

import pandas
from sqlalchemy.engine import Engine

from buhtuh.expression import Expression
from buhtuh.types import get_series_type_from_dtype, get_dtype_from_db_dtype
from sql_models.model import SqlModel, CustomSqlModel
from sql_models.sql_generator import to_sql

if TYPE_CHECKING:
    from buhtuh.partitioning import BuhTuhWindow, BuhTuhGroupBy
    from buhtuh.series import BuhTuhSeries, BuhTuhSeriesBoolean, BuhTuhSeriesAbstractNumeric

DataFrameOrSeries = Union['BuhTuhDataFrame', 'BuhTuhSeries']
ColumnNames = Union[str, List[str]]


class SortColumn(NamedTuple):
    expression: Expression
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
        group_by: Optional['BuhTuhGroupBy'],
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
        self._group_by = group_by
        self._order_by = order_by if order_by is not None else []
        for key, value in series.items():
            if key != value.name:
                raise ValueError(f'Keys in `series` should match the name of series. '
                                 f'key: {key}, series.name: {value.name}')
            if value.index != self._index:
                raise ValueError(f'Indices in `series` should match dataframe. '
                                 f'df: {value.index}, series.index: {self._index}')
            self._data[key] = value
        for value in index.values():
            if value.index != {}:
                raise ValueError('Index series can not have non-empty index property')

        if group_by is not None:
            if group_by.index != index:
                raise ValueError('Index should match group_by index')

        if set(index.keys()) & set(series.keys()):
            raise ValueError(f"The names of the index series and data series should not intersect. "
                             f"Index series: {sorted(index.keys())} data series: {sorted(series.keys())}")

    def copy_override(
            self,
            engine: Engine = None,
            base_node: SqlModel = None,
            index: Dict[str, 'BuhTuhSeries'] = None,
            series: Dict[str, 'BuhTuhSeries'] = None,
            group_by: List[Union['BuhTuhGroupBy', None]] = None,  # List so [None] != None
            order_by: List[SortColumn] = None) -> 'BuhTuhDataFrame':
        """
        Create a copy of self, with the given arguments overriden

        Big fat warning: group_by can legally be None, but if you want to set that,
        set the param in a list: [None], or [someitem]. If you set None, it will be left alone.
        """
        return BuhTuhDataFrame(
            engine=engine if engine is not None else self.engine,
            base_node=base_node if base_node is not None else self._base_node,
            index=index if index is not None else self._index,
            series=series if series is not None else self._data,
            group_by=self._group_by if group_by is None else group_by[0],
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

    @property
    def group_by(self):
        return copy(self._group_by)

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
            self._group_by == other._group_by and \
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
            group_by=None,
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
        dtypes = {str(column_name): dtype.name for column_name, dtype in df_copy.dtypes.items()
                  if column_name in df.columns}
        unsupported_dtypes = {str(column_name): dtype for column_name, dtype in dtypes.items()
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
            dtypes=dtypes,
            group_by=None
        )

    @classmethod
    def get_instance(
            cls,
            engine,
            base_node: SqlModel,
            index_dtypes: Dict[str, str],
            dtypes: Dict[str, str],
            group_by: Optional['BuhTuhGroupBy'],
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
                index={},  # Empty index for index series
                name=key,
                expression=Expression.column_reference(key),
                group_by=group_by
            )
        series: Dict[str, BuhTuhSeries] = {}
        for key, value in dtypes.items():
            series_type = get_series_type_from_dtype(value)
            series[key] = series_type(
                engine=engine,
                base_node=base_node,
                index=index,
                name=key,
                expression=Expression.column_reference(key),
                group_by=group_by
            )
        return BuhTuhDataFrame(
            engine=engine,
            base_node=base_node,
            index=index,
            series=series,
            group_by=group_by,
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
            group_by=None,
            order_by=[]
        )

    def __getitem__(self,
                    key: Union[str, List[str], Set[str], slice, 'BuhTuhSeriesBoolean']) -> DataFrameOrSeries:
        """
        TODO: Comments
        :param key:
        :return:
        """
        from buhtuh.series import BuhTuhSeriesBoolean

        if isinstance(key, str):
            # if this series is detached from the df, make sure it remembers its aggregation
            return self.data[key].copy_override(group_by=[self._group_by])
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
            if self._group_by is not None:
                raise NotImplementedError("HAVING is not implemented yet")

            # We only support first level boolean indices for now
            if key.base_node != self.base_node:
                raise ValueError('Cannot apply Boolean series with a different base_node to DataFrame.'
                                 'Hint: make sure the Boolean series is derived from this DataFrame. '
                                 'Alternative: use df.merge(series) to merge the series with the df first,'
                                 'and then create a new Boolean series on the resulting merged data.')
            model_builder = CustomSqlModel(
                name='boolean_selection',
                sql='select {index}, {columns} from {{_last_node}} where {where}'
            )
            model = model_builder(
                columns=self._get_all_column_expressions(),
                index=self._get_all_index_expressions(),
                _last_node=self.base_node,
                where=key.expression.resolve_column_references(),
            )
            return self._df_or_series(
                BuhTuhDataFrame.get_instance(
                    engine=self.engine,
                    base_node=model,
                    index_dtypes={name: series.dtype for name, series in self.index.items()},
                    dtypes={name: series.dtype for name, series in self.data.items()},
                    group_by=None,
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
        from buhtuh.series import BuhTuhSeries, const_to_series
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
                    if self._group_by != value.group_by:
                        raise ValueError(f'GroupBy of assigned value does not match DataFrame. '
                                         f'Value: {value.group_by}, df: {self._group_by}')
                    # unset group_by as we are now "responsible" for it again
                    self._data[key] = value.copy_override(name=key, group_by=[None])
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

    def rename(self, mapper: Union[Dict[str, str], Callable[[str], str]] = None,
               index: Union[Dict[str, str], Callable[[str], str]] = None,
               columns: Union[Dict[str, str], Callable[[str], str]] = None,
               axis: int = 0,
               inplace: bool = False,
               level: int = None,
               errors: str = 'ignore'):
        """
        Rename columns.

        The interface is similar to Panda's DataFrame.rename(). However we don't support renaming indexes, so
            recommended usage is `rename(columns=...)`
        :param: mapper: please use columns
        :param: index: not supported
        :param: columns: dict str:str to rename columns, or a function that takes column
            names as an argument and returns the new one. The new column names must not clash with other
            column names in either self.data or self.index, after renaming is complete.
        :param: axis: axis = 1 is supported, rest is not.
        :param: inplace: update this df or make a copy first
        :param: level: not supported
        :param: errors: Either 'ignore' or 'raise'. When set to 'ignore' KeyErrors about non-existing
            column names in `columns` or `mapper` are ignored. Errors thrown in the mapper function or about
            invalid target column names are not suppressed.
        :note: copy parameter is not supported since it makes very little sense for db backed series
        """
        if level is not None or\
            index is not None or\
                (mapper is not None and axis == 0):
            raise NotImplementedError("index renames not supported")

        if mapper is not None:
            columns = mapper

        if inplace:
            df = self
        else:
            df = self.copy_override()

        if callable(columns):
            columns = {source: columns(source) for source in df.data_columns}

        if not isinstance(columns, dict):
            raise TypeError(f'unsupported argument type for columns or mappers: {type(columns)}')

        non_existing_columns = set(columns.keys()) - set(df.data.keys())
        if errors == 'raise' and non_existing_columns:
            raise KeyError(f'No such column(s): {non_existing_columns}')

        from buhtuh.series import BuhTuhSeries
        new_data: Dict[str, 'BuhTuhSeries'] = {}
        for column_name in df.data_columns:
            new_name = columns.get(column_name, column_name)
            if new_name in df.index or new_name in new_data:
                # This error doesn't happen in Pandas, as Pandas allows duplicate column names, but we don't.
                raise ValueError(f'Cannot set {column_name} as {new_name}. New column name already exists.')
            series = df.data[column_name]
            if new_name != series.name:
                series = series.copy_override(name=new_name)
            new_data[new_name] = series
        df._data = new_data
        return df

    def __delitem__(self, key: str):
        """ TODO: comments """
        if isinstance(key, str):
            del(self._data[key])
            return
        else:
            raise TypeError(f'Unsupported type {type(key)}')

    def drop(self,
             labels: List[str] = None,
             index: List[str] = None,
             columns: List[str] = None,
             level: int = None,
             inplace: bool = False,
             errors: str = 'raise') -> 'BuhTuhDataFrame':
        """
        Drop labels/columns from the dataframe

        :param: labels: not supported
        :param: index: not supported
        :param: columns: the list of columns to drop
        :param: level: not supported
        :param: inplace: whether to update this df of make a copy first
        :param: errors: 'raise' or 'ignore' missing key errors
        """
        if labels or index is not None:
            # TODO we could do this using a boolean __series__
            raise NotImplementedError('dropping labels from index not supported.')

        if level is not None:
            raise NotImplementedError('dropping index levels not supported.')

        if columns is None:
            raise ValueError("columns needs to be an (empty) list of strings.")

        if inplace:
            df = self
        else:
            df = self.copy_override()

        try:
            for key in columns:
                del(df[key])
        except Exception as e:
            if errors == "raise":
                raise e

        return df

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

    def _partition_by_series(self,
                             by: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None],
                             ) -> List['BuhTuhSeries']:
        """
        Helper method to check and compile a partitioning list
        """
        from buhtuh.series import BuhTuhSeries
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
            by: Union[str, 'BuhTuhSeries',
                      List[Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']]]],
                      None] = None
    ) -> 'BuhTuhDataFrame':
        """
        Group by any of the series currently in this dataframe, both from index
        as well as data.
        :param by: The series to group by. Supported are: a str containing a series name,
            a series, or a list of those. If `by` is a list of lists, we'll create a grouping set,
            else a normal group by will be created.
        :note: if the dataframe is already grouped, we'll create a grouping list from the initial
            grouping combined with this one.
        :return: an object to perform aggregations on
        """
        from buhtuh.partitioning import BuhTuhGroupBy, BuhTuhGroupingList, BuhTuhGroupingSet

        group_by: BuhTuhGroupBy
        if isinstance(by, list) and len([b for b in by if isinstance(b, list)]) > 0:
            # by is a list containing at least one other list. We're creating a grouping set
            # aka "Yo dawg, I heard you like GroupBys, ..."
            group_by = BuhTuhGroupingSet(
                [BuhTuhGroupBy(engine=self.engine,
                               base_node=self.base_node,
                               group_by_columns=self._partition_by_series(b))
                 for b in by]
            )
        else:
            by_mypy = cast(Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None],
                           by)
            group_by = BuhTuhGroupBy(engine=self.engine, base_node=self.base_node,
                                     group_by_columns=self._partition_by_series(by_mypy))

        # if there already was a group_by, combine into list
        if self._group_by:
            group_by = BuhTuhGroupingList([self._group_by, group_by])

        data = [s for n, s in self.all_series.items() if n not in group_by.index]
        return group_by.to_frame(data, materialized=False)

    def window(self,
               by: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None] = None,
               **frame_args) -> 'BuhTuhDataFrame':
        """
        Create a window on the current dataframe and its sorting.
        TODO Better argument typing, needs fancy import logic
        :see: BuhTuhWindow __init__ for frame args
        """
        from buhtuh.partitioning import BuhTuhWindow
        index = self._partition_by_series(by)
        window = BuhTuhWindow(engine=self.engine, base_node=self.base_node,
                              group_by_columns=index,
                              order_by=self._order_by,
                              **frame_args)
        data = [s for n, s in self.all_series.items() if n not in window.index]
        return window.to_frame(data, materialized=False)

    def cube(self,
             by: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None] = None,
             ) -> 'BuhTuhDataFrame':
        """
        Create a cube on any of the series currently in this dataframe, both from index
        as well as data.
        :see: BuhTuhCube for more info
        """
        from buhtuh.partitioning import BuhTuhCube
        index = self._partition_by_series(by)
        cube = BuhTuhCube(engine=self.engine, base_node=self.base_node, group_by_columns=index)
        data = [s for n, s in self.all_series.items() if n not in cube.index]
        return cube.to_frame(data, materialized=False)

    def rollup(self,
               by: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None] = None,
               ) -> 'BuhTuhDataFrame':
        """
        Create a rollup on any of the series currently in this dataframe, both from index
        as well as data.
        :see: BuhTuhRollup for more info
        """
        from buhtuh.partitioning import BuhTuhRollup
        index = self._partition_by_series(by)
        rollup = BuhTuhRollup(engine=self.engine, base_node=self.base_node,
                              group_by_columns=index)
        data = [s for n, s in self.all_series.items() if n not in rollup.index]
        return rollup.to_frame(data, materialized=False)

    def rolling(self, window: int,
                min_periods: int = None,
                center: bool = False,
                on: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None] = None,
                closed: str = 'right') -> 'BuhTuhDataFrame':
        """
        A rolling window of size 'window', by default right aligned

        :param: window: the window size
        :param: min_periods: the min amount of rows included in the window before an actual value is
                returned
        :param: center: center the result, or align the result on the right
        :param: on: the partition to use, see window()
        :param: closed:  Make the interval closed on the ‘right’, ‘left’, ‘both’ or ‘neither’
                endpoints. Defaults to ‘right’, and the rest is currently unsupported.
        :note:  win_type,axis and method parameters as supported by pandas, are currently not implemented.
        :note:  the `on` parameter behaves differently from pandas, where it can be use to select to series
                to iterate over.
        """
        from buhtuh.partitioning import BuhTuhWindowFrameBoundary, BuhTuhWindowFrameMode, \
            BuhTuhWindow

        if min_periods is None:
            min_periods = window

        if min_periods > window:
            raise ValueError(f'min_periods {min_periods} must be <= window {window}')

        if closed != 'right':
            raise NotImplementedError("Only closed=right is supported")

        mode = BuhTuhWindowFrameMode.ROWS
        end_value: Optional[int]
        if center:
            end_value = (window - 1) // 2
        else:
            end_value = 0

        start_boundary = BuhTuhWindowFrameBoundary.PRECEDING
        start_value = (window - 1) - end_value

        if end_value == 0:
            end_boundary = BuhTuhWindowFrameBoundary.CURRENT_ROW
            end_value = None
        else:
            end_boundary = BuhTuhWindowFrameBoundary.FOLLOWING

        index = self._partition_by_series(on)
        group_by = BuhTuhWindow(engine=self.engine, base_node=self.base_node,
                                group_by_columns=index,
                                order_by=self._order_by,
                                mode=mode,
                                start_boundary=start_boundary, start_value=start_value,
                                end_boundary=end_boundary, end_value=end_value,
                                min_values=min_periods)
        data = [s for n, s in self.all_series.items() if n not in group_by.index]
        return group_by.to_frame(data, materialized=False)

    def expanding(self,
                  min_periods: int = 1,
                  center: bool = False,
                  on: Union[str, 'BuhTuhSeries', List[Union[str, 'BuhTuhSeries']], None] = None,
                  ) -> 'BuhTuhDataFrame':
        """
        Create an expanding window starting with the first row in the group, with at least min_period
        observations. The result will be right-aligned in the window

        :param: min_periods:    The minimum amount of observations in the window before a value is reported
        :param: center:         Whether to center the result, currently not supported
        :param: on:             The partition that will be applied. Note: this is different from pandas, where
                                The partition is determined earlier in the process.
        """
        # TODO We could move the partitioning to BuhTuhGroupBy
        from buhtuh.partitioning import BuhTuhWindowFrameBoundary, BuhTuhWindowFrameMode, \
            BuhTuhWindow

        if center:
            # Will never be implemented probably, as it's also deprecated in pandas
            raise NotImplementedError("centering is not implemented.")

        mode = BuhTuhWindowFrameMode.ROWS
        start_boundary = BuhTuhWindowFrameBoundary.PRECEDING
        start_value = None
        end_boundary = BuhTuhWindowFrameBoundary.CURRENT_ROW
        end_value = None

        index = self._partition_by_series(on)
        window = BuhTuhWindow(engine=self.engine, base_node=self.base_node,
                              group_by_columns=index,
                              order_by=self._order_by,
                              mode=mode,
                              start_boundary=start_boundary, start_value=start_value,
                              end_boundary=end_boundary, end_value=end_value,
                              min_values=min_periods)
        data = [s for n, s in self.all_series.items() if n not in window.index]
        return window.to_frame(data, materialized=False)

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
        order_by = [SortColumn(expression=by_series.expression, asc=asc_item)
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

    def get_order_by_expression(self) -> Expression:
        """
        Get a properly formatted order by clause based on this df's order_by.
        Will return an empty string in case ordering in not requested.
        """
        if self._order_by:
            exprs = [sc.expression for sc in self._order_by]
            fmtstr = [f"{{}} {'asc' if sc.asc else 'desc'}" for sc in self._order_by]
            return Expression.construct(f'order by {", ".join(fmtstr)}', *exprs)
        else:
            return Expression.construct('')

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
            sql='select {index}, {columns} from {{_last_node}} {order} {limit}'
        )

        return model_builder(
            columns=self._get_all_column_expressions(),
            index=self._get_all_index_expressions(),
            _last_node=self.base_node,
            limit=Expression.construct('' if limit_str is None else f'{limit_str}'),
            order=self.get_order_by_expression().resolve_column_references()
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

    def _get_all_index_expressions(self, table_name: str = None) -> Sequence[Expression]:
        return [Expression.column_reference(index_column).resolve_column_references(table_name)
                for index_column in self.index.keys()]

    def _get_all_column_expressions(self, table_name: str = None) -> Sequence[Expression]:
        return [series.get_column_expression().resolve_column_references(table_name)
                for series in self.data.values()]

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

    def _apply_func_to_series(self,
                              func: Union[str, Callable, List[Union[str, Callable]],
                                          Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
                              axis: int = 1,
                              numeric_only: bool = False,
                              exclude_non_applied: bool = False,
                              *args, **kwargs) -> List['BuhTuhSeries']:
        """
        :param func: function, str, list or dict to apply to all series
            Function to use on the data. If a function, must work when passed a
            BuhTuhSeries.

            Accepted combinations are:
            - function
            - string function name
            - list of functions and/or function names, e.g. [BuhTuhSeriesInt64.sum, 'mean']
            - dict of axis labels -> functions, function names or list of such.
        :param axis: the axis
        :param numeric_only: Whether to apply to numeric series only, or attempt all.
        :param exclude_non_applied: Exclude series where applying was not attempted / failed
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function
        :note: Pandas has numeric_only=None to attempt all columns but ignore failing ones
            silently. This is currently not implemented.
        :note: axis defaults to 1, because 0 is currently unsupported
        """
        from buhtuh.series import BuhTuhSeriesAbstractNumeric
        if axis == 0:
            raise NotImplementedError("Only axis=1 is currently implemented")

        if numeric_only is None:
            raise NotImplementedError("numeric_only=None to attempt all columns but ignore "
                                      "failing ones silently is currently not implemented.")

        apply_dict: Dict[str, List[Union[str, Callable]]] = {}
        if isinstance(func, dict):
            # make sure the keys are series we know
            for k, v in func.items():
                if k not in self._data:
                    raise KeyError(f'{k} not found in group by series')
                if isinstance(v, str) or callable(v):
                    apply_dict[k] = [v]
                elif isinstance(v, list):
                    apply_dict[k] = v
                else:
                    raise TypeError(f'Unsupported value type {type(func)} in func dict for key {k}')
        elif isinstance(func, (str, list)) or callable(func):
            apply_dict = {}
            # check whether we need to exclude non-numeric
            for name, series in self.data.items():
                if numeric_only and not isinstance(series, BuhTuhSeriesAbstractNumeric):
                    continue
                if isinstance(func, list):
                    apply_dict[name] = func
                else:
                    apply_dict[name] = [func]
        else:
            raise TypeError(f'Unsupported type for func: {type(func)}')

        new_series = {}
        for name, series in self._data.items():
            if name not in apply_dict:
                if not exclude_non_applied:
                    new_series[name] = series.copy_override()
                continue
            for applied in series.apply_func(apply_dict[name], *args, **kwargs):
                if applied.name in new_series:
                    raise ValueError("duplicate result series: {applied.name}")
                new_series[applied.name] = applied

        return list(new_series.values())

    def apply_func(self, func: Union[str, Callable, List[Union[str, Callable]],
                                     Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
                   axis: int = 1,
                   numeric_only: bool = False,
                   exclude_non_applied: bool = False,
                   *args, **kwargs) -> 'BuhTuhDataFrame':
        """ see apply_to_series() """
        series = self._apply_func_to_series(func, axis, numeric_only,
                                            exclude_non_applied, *args, ** kwargs)
        return cast('BuhTuhDataFrame', self.copy_override(series={s.name: s for s in series}))

    def aggregate(self,
                  func: Union[str, Callable, List[Union[str, Callable]],
                              Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
                  axis: int = 1,
                  numeric_only: bool = False,
                  *args, **kwargs) -> 'BuhTuhDataFrame':
        """
        use agg(..)
        """
        return self.agg(func, axis, numeric_only, *args, **kwargs)

    def agg(self,
            func: Union[str, Callable, List[Union[str, Callable]],
                        Dict[str, Union[str, Callable, List[Union[str, Callable]]]]],
            axis: int = 1,
            numeric_only: bool = False,
            *args,
            **kwargs) -> 'BuhTuhDataFrame':
        """
        :param func: the aggregations to apply on all series.
            See apply_func() for supported arguments
        :param axis: the aggregation axis
        :param numeric_only: Whether to aggregate numeric series only, or attempt all.
        :param group_by: The grouping to use, defaults to entire dataframe
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function
        :note: Pandas has numeric_only=None to attempt all columns but ignore failing ones
            silently. This is currently not implemented.
        :note: axis defaults to 1, because 0 is currently unsupported
        """
        from buhtuh.partitioning import BuhTuhGroupBy
        group_by = BuhTuhGroupBy(self.engine, self.base_node, []) \
            if self._group_by is None else self._group_by
        series = self._apply_func_to_series(func, axis, numeric_only,
                                            True,  # exclude_non_applied, must be positional arg.
                                            group_by, *args, **kwargs)
        return group_by.to_frame(series)

    def _aggregate_func(self, func, axis, level, numeric_only, *args, **kwargs):
        if level is not None:
            raise NotImplementedError("index levels are currently not implemented")
        return self.agg(func, axis, numeric_only, *args, **kwargs)

    # AGGREGATES
    def count(self, axis=None, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('count', axis, level, numeric_only, **kwargs)

    def kurt(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('kurt', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def kurtosis(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('kurtosis', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def mad(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('mad', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def max(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('max', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def min(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('min', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def mean(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('mean', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def median(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('median', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def mode(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        # slight deviation from pd.mode(axis=0, numeric_only=False, dropna=True)
        return self._aggregate_func('mode', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def nunique(self, axis=None, skipna=True, **kwargs):
        # deviation from horrible pd.nunique(axis=0, dropna=True)
        return self._aggregate_func('nunique', axis=axis,
                                    level=None, numeric_only=False, skipna=skipna, **kwargs)

    def skew(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
        return self._aggregate_func('skew', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def prod(self, axis=None, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
        return self._aggregate_func('prod', axis, level, numeric_only,
                                    skipna=skipna, min_count=min_count, **kwargs)

    def product(self, axis=None, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
        return self._aggregate_func('product', axis, level, numeric_only,
                                    skipna=skipna, min_count=min_count, **kwargs)

    def sem(self, axis=None, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        return self._aggregate_func('sem', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def std(self, axis=None, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        return self._aggregate_func('std', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def sum(self, axis=None, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
        return self._aggregate_func('sum', axis, level, numeric_only,
                                    skipna=skipna, min_count=min_count, **kwargs)

    def var(self, axis=None, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        return self._aggregate_func('var', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)
