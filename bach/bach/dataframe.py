"""
Copyright 2021 Objectiv B.V.
"""
from copy import copy

from typing import (
    List, Set, Union, Dict, Any, Optional, Tuple,
    cast, NamedTuple, TYPE_CHECKING, Callable, Hashable, Sequence, overload, Mapping,
)

import numpy
import pandas
from sqlalchemy.engine import Engine

from bach.expression import Expression, SingleValueExpression, VariableToken
from bach.from_database import get_dtypes_from_table, get_dtypes_from_model
from bach.sql_model import BachSqlModel, CurrentNodeSqlModel, get_variable_values_sql
from bach.types import get_series_type_from_dtype, AllSupportedLiteralTypes, StructuredDtype
from bach.utils import (
    escape_parameter_characters, validate_node_column_references_in_sorting_expressions, SortColumn
)
from sql_models.constants import NotSet, not_set
from sql_models.graph_operations import update_placeholders_in_graph, get_all_placeholders
from sql_models.model import SqlModel, Materialization, CustomSqlModelBuilder, RefPath

from sql_models.sql_generator import to_sql
from sql_models.util import quote_identifier, is_bigquery, DatabaseNotSupportedException, is_postgres

if TYPE_CHECKING:
    from bach.partitioning import Window, GroupBy
    from bach.savepoints import Savepoints
    from bach.series import Series, SeriesBoolean

# TODO exclude from docs
DataFrameOrSeries = Union['DataFrame', 'Series']
# ColumnNames: a single column name, or a list of column names
# TODO exclude from docs
ColumnNames = Union[str, List[str]]
# TODO exclude from docs
ColumnFunction = Union[str, Callable, List[Union[str, Callable]]]
# ColumnFunction: Identifier for a function that can be applied to a column, possibly in the context of a
#     window or aggregation.
#     Accepted combinations are:
#     - function
#     - string function name
#     - list of functions and/or function names, e.g. [SeriesInt64.sum, 'mean']
#     - dict of axis labels -> functions, function names or list of such.

Level = Union[int, List[int], str, List[str]]


class DtypeNamePair(NamedTuple):
    dtype: str  # TODO: make 'dtype' a type instead of using str
    name: str


class DefinedVariable(NamedTuple):
    name: str
    dtype: str
    value: Optional[Hashable]
    ref_path: Optional[RefPath]
    old_value: Optional[Hashable]


class DataFrame:
    """
    A mutable DataFrame representing tabular data in a database and enabling operations on that data.

    A Bach DataFrame object can be used to process large amounts of data on a database, while using an api
    that is based on the pandas api. This allows the database to group and aggregate data, sample data and
    do other operations that are not suitable for in memory processing. At any time it is possible to write
    your Bach DataFrame to a pandas DataFrame.

    **Usage**

    It should generally not be required to construct DataFrame instances manually. A DataFrame can be
    constructed using the any of the bach classmethods like :py:meth:`from_table`, :py:meth:`from_model`, or
    :py:meth:`from_pandas`. The returned DataFrame can be thought of as a dict-like container for Bach
    Series objects.

    **Getting & Setting columns**

    Getting data works similar to pandas DataFrame. Single columns can be retrieved with ``df['column_name']``
    as well as ``df.column_name``. This will return a single Bach Series. Multiple columns can be retrieved by
    passing a list of column names like: ``df[['column_name','other_column_name']]``. This returns a Bach
    DataFrame.

    A selection of rows can be selected with python slicing. I.e. ``df[2:5]`` returns row 2 to 5. Only
    positive integers are currently accepted in slices.

    SeriesBoolean can also be used to filter DataFrames, and these Series are easily created using comparison
    operations like equals (`==`), less-than (`<`), not(`~`) on two series, or series with values:
    ``boolean_series = a == b``. Boolean indexing can be done like ``df[df.column == 5]``. Only rows are
    returned for which the condition is true.

    Label-based selection is also supported by using the ``.loc`` attribute. Each label is interpreted
    as a value contained by the index column. Unlike Pandas, if the label is not found,
    no exception will be raised. I.e. ``df.loc['a']`` returns rows where the index series is equal to ``a``.
    Slicing can also be performed (the dataframe must be sorted). I.e. ``df['a':'d', 'col1:col3']``. This will
    return all rows/columns included in the slicing, where the start and stop are inclusive.
    For more information about label-based selection, please take a look to :py:attr:`loc`.


    **Moving Series around**

    Values, Series or DataFrames can be set to another DataFrame. Setting Series or DataFrames to another
    DataFrame is possible if they share the same base node or index dtype. DataFrames and Series share the
    same base node if they originate from the same data source. In most cases this means that the series
    that is to be set to the DataFrame is a result of operations on the DataFrame that is started with.
    If a Series or DataFrame do not share the same base node, the new column is or columns are set using a
    merge on the index. This works for one level indexes where the dtype of the series is the same as the
    DataFrame's index dtype.

    **Examples**

    .. code-block:: python

        df['a'] = df.column_name + 5
        df['b'] = ''


    **Database access**

    The data of this DataFrame is always held in the database and operations on the data are performed
    by the database, not in local memory. Data will only be transferred to local memory when an
    explicit call is made to one of the functions that transfers data:

    * :py:meth:`head`
    * :py:meth:`to_pandas`
    * :py:meth:`to_numpy`
    * :py:meth:`get_sample`
    * The property accessors :py:attr:`Series.value` (Series only), :py:attr:`values`

    Other functions will not transfer data, nor will they trigger any operations to run on the database.
    Operations on the DataFrame are combined and translated to a single SQL query, which is executed
    only when one of the above mentioned data-transfer functions is called.

    The API of this DataFrame is partially compatible with Pandas DataFrames. For more on Pandas
    DataFrames see https://pandas.pydata.org/docs/reference/frame.html
    """
    # todo note on ordering for slices?
    # todo 'meaning that they originate from the same data source' ok, by approximation
    # todo _get_dtypes also queries the database

    # A DataFrame holds the state of a set of operations on it's base node
    #
    # The main components in this are the dicts of Series that it keeps: `index` and `data`
    # The `data` Series represent all data columns, possibly waiting for aggregation.
    # The `index` Series are used as an index in key lookups, but serve no other purpose but for nice
    # visualisation when converting to pandas Dataframes.
    #
    # When a Series is used as an index, it should be free from any pending aggregation (and thus
    # `Series.group_by` should be None, and its `Series.index` should be `{}`.
    #
    # `DataFrame.group_by` should always match the `Series.group_by` for all Series in the `data` dict.
    #  (and `Series.index` should match `Series.group_by.index`, but that's checked in `Series.__init__`)
    #
    # To illustrate (copied verbatim from Series docs):
    # The rule here: If a series needs a `group_by` to be evaluated, then and only then it should carry that
    # `group_by`. This implies that index Series coming from `GroupBy.index`, do not carry that `group_by`.
    # Only the data Series that actually need the aggregation to happen do.
    #
    # Order is also tracked in `order_by`. It can either be None or a list of SortColumns. Ordering is mostly
    # kept throughout operations, but for example materialization resets the sort order.
    def __init__(
            self,
            engine: Engine,
            base_node: BachSqlModel,
            index: Dict[str, 'Series'],
            series: Dict[str, 'Series'],
            group_by: Optional['GroupBy'],
            order_by: Optional[List[SortColumn]],
            savepoints: 'Savepoints',
            variables: Dict['DtypeNamePair', Hashable] = None
    ):
        """
        Instantiate a new DataFrame.
        There are utility class methods to easily create a DataFrame from existing data such as a
        table (:py:meth:`from_table`), an already instantiated sql-model (:py:meth:`from_model`), or a
        pandas dataframe (:py:meth:`from_pandas`).

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
        self._data: Dict[str, Series] = {}
        self._group_by = group_by
        self._order_by = order_by if order_by is not None else []
        self._savepoints = savepoints
        self._variables = variables if variables else {}
        for key, value in series.items():
            if key != value.name:
                raise ValueError(f'Keys in `series` should match the name of series. '
                                 f'key: {key}, series.name: {value.name}')
            if not dict_name_series_equals(value.index, index):
                raise ValueError(f'Indices in `series` should match dataframe. '
                                 f'df: {value.index}, series.index: {index}')
            if value.group_by != group_by:
                raise ValueError(f'Group_by in `series` should match dataframe. '
                                 f'df: {group_by}, series.group_by: {value.group_by}')
            if value.base_node != base_node:
                raise ValueError(f'Base_node in `series` should match dataframe. '
                                 f'df: {base_node}, series.base_node: {value.base_node}')

            self._data[key] = value

        for value in index.values():
            if value.index != {}:
                raise ValueError('Index series can not have non-empty index property')
            if value.group_by:
                raise ValueError('Index series can not have a group_by')

        if group_by is not None and not dict_name_series_equals(group_by.index, index):
            raise ValueError('Index should match group_by index')

        if set(index.keys()) & set(series.keys()):
            raise ValueError(f"The names of the index series and data series should not intersect. "
                             f"Index series: {sorted(index.keys())} data series: {sorted(series.keys())}")

        validate_node_column_references_in_sorting_expressions(node=base_node, order_by=self.order_by)

    @property
    def engine(self):
        """
        INTERNAL: Get the current engine
        """
        return self._engine

    @property
    def base_node(self) -> BachSqlModel:
        """
        INTERNAL: Get the current base node
        """
        return self._base_node

    @property
    def index(self) -> Dict[str, 'Series']:
        """
        Get the index dictionary `{name: Series}`
        """
        return copy(self._index)

    @property
    def data(self) -> Dict[str, 'Series']:
        """
        Get the data dictionary `{name: Series}`
        """
        return copy(self._data)

    @property
    def order_by(self) -> List[SortColumn]:
        """
        Get the current sort order, if any.
        """
        return copy(self._order_by)

    @property
    def savepoints(self) -> 'Savepoints':
        return self._savepoints

    @property
    def variables(self) -> Dict[DtypeNamePair, Hashable]:
        """
        Get all variables for which values are set, which will be used when querying the database.

        Note that there might also be variables defined earlier in self.base_node, that already have a value.
        Those variables values will not be changed, unless they are listed here. To get an overview of all
        variables on which the values in this DataFrame depend use :meth:`get_all_defined_variables()`
        """
        return copy(self._variables)

    @property
    def all_series(self) -> Dict[str, 'Series']:
        """
        Get all index and data Series in a dictionary `{name: Series}`
        """
        return {**self.index, **self.data}

    @property
    def index_columns(self) -> List[str]:
        """
        Get all the index columns' names in a List
        """
        return list(self.index.keys())

    @property
    def data_columns(self) -> List[str]:
        """
        Get all the data Series' names in a List
        """
        return list(self.data.keys())

    # alias for getting data names
    columns = data_columns

    @property
    def index_dtypes(self) -> Dict[str, str]:
        """
        Get the index Series' dtypes in a dictionary `{name: dtype}`
        """
        return {column: data.dtype for column, data in self.index.items()}

    @property
    def dtypes(self) -> Dict[str, str]:
        """
        Get the data Series' dtypes in a dictionary `{name: dtype}`
        """
        return {column: data.dtype for column, data in self.data.items()}

    @property
    def group_by(self) -> Optional['GroupBy']:
        """
        Get this DataFrame's grouping, if any.

        If `group_by` is not None, the DataFrame can be used to perform aggregations on.
        """
        return copy(self._group_by)

    @property
    def is_materialized(self) -> bool:
        """
        Return true if this DataFrame is in a materialized state, i.e. all information about the
        DataFrame's values is encoded in self.base_node.

        A DataFrame that's freshly constructed with :py:meth:`from_table`,
        :py:meth:`from_model`, or :py:meth:`from_pandas` will be in a materialized state. Operations on such
        a DataFrame will change it to be not materialized. Calling :py:meth:`materialize` on a
        non-materialized DataFrame will return a new DataFrame that is materialized.

        TODO: a known problem is that DataFrames with 'json_postgres' columns are never in a materialized
         state, and cannot be materialized with materialize()

        :returns: True if this DataFrame is in a materialized state, False otherwise
        """
        if self.group_by or self.order_by:
            return False
        if tuple(self.all_series.keys()) != self.base_node.columns:
            return False
        for name, series in self.all_series.items():
            if series.expression != Expression.column_reference(name):
                return False
        return True

    @property
    def loc(self):
        """
        The ``.loc`` accessor offers different methods for label-based selection. The following are
        valid use-cases:

        **Examples**

        .. testsetup:: loc
           :skipif: engine is None

           import pandas
           data = {'index': ['a', 'b', 'c', 'd'], 'values': [1, 2, 3, 4]}
           pdf = pandas.DataFrame(data)

           df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
           df = df.set_index('index')

        .. doctest:: loc
            :skipif: engine is None


            >>> df.to_pandas()
                   values
            index
            a           1
            b           2
            c           3
            d           4

        **Getting Values**

        **Single-label selection**: Returns all rows where the index column is equal to the label.
        This returns a Bach Series, where all selected columns are stacked as a single index column.

        .. doctest:: loc
            :skipif: engine is None


            >>> df.loc['a'].to_pandas()
            __stacked_index
            values    1
            Name: __stacked, dtype: int64


        **List-label selection**: Returns all rows where the index column is equal to any of
        the labels to be selected. Returns a Bach DataFrame.

        .. doctest:: loc
            :skipif: engine is None

            >>> df.loc[['a', 'b']].to_pandas()
                   values
            index
            a           1
            b           2

        **Slicing selection by labels**: Returns all rows between the start and stop of the slice
        (start and stop are inclusive).

        .. doctest:: loc
            :skipif: engine is None

            >>> df = df.sort_index()  # slicing is supported only when frame is sorted
            >>> df.loc['a':'c'].to_pandas()
                   values
            index
            a           1
            b           2
            c           3

        **Slicing by series boolean**: Returns all rows where the series boolean
        is true.

        .. doctest:: loc
            :skipif: engine is None

            >>> df.loc[df['values'] == 2].to_pandas()
                   values
            index
            b           2

        For each of the previous types of selection, column selection is supported,
        this can be by just passing a label, list of labels or a slice. For example:

        .. doctest:: loc
            :skipif: engine is None

            >>> df['extra_col'] = 1
            >>> df.loc['a', 'extra_col'].to_pandas()
            __stacked_index
            extra_col    1
            Name: __stacked, dtype: int64


        **Setting Values**

        **Set values for an entire row**: Will modify all columns where index is matched.

        .. doctest:: loc
            :skipif: engine is None

            >>> df.loc['a'] = 2
            >>> df.to_pandas()
                   values  extra_col
            index
            a           2          2
            b           2          1
            c           3          1
            d           4          1

        **Set values for multiple rows and specific columns**: Modifies only the passed columns.

        .. doctest:: loc
            :skipif: engine is None

            >>> df.loc[['b', 'd'], 'values'] = 10
            >>> df.to_pandas()
                   values  extra_col
            index
            a           2          2
            b          10          1
            c           3          1
            d          10          1

        **Set values for row slice**: Modifies all rows included in the slice.

        .. doctest:: loc
            :skipif: engine is None

            >>> df.loc['a':'c', 'values'] = 3
            >>> df.to_pandas()
                    values   extra_col
            index
            a           3           2
            b           3           1
            c           3           1
            d          10           1

        .. note::
            * .loc supports access-only for first-level index.
            * Slicing rows is supported-only when the dataframe is sorted.
        """
        from bach.indexing import LocIndexer
        return LocIndexer(self)

    @property
    def plot(self):
        """
        The ``.plot`` accessor offers different methods for data visualization. Data is preprocessed based
        on the kind of plot and draws image directly using Pandas ``DataFrame.plot``:

        .. note::
            - See pandas documentation online for more information.
            - Each plotting method queries the database.
        """
        from bach.plotting import PlotHandler
        return PlotHandler(self)

    def __eq__(self, other: Any) -> bool:
        """
        Compares two DataFrames for equality.
        Compares all fields that (potentially) influence the values of the data represented by the DataFrame,
        i.e. all fields except for self.savepoints
        """
        if not isinstance(other, DataFrame):
            return False
        # We cannot just compare the data and index properties, because the Series objects have
        # overridden the __eq__ function in a way that makes normal comparisons not useful. We have to use
        # equals() instead
        return \
            dict_name_series_equals(self.index, other.index) and \
            dict_name_series_equals(self.data, other.data) and \
            self.engine == other.engine and \
            self.base_node == other.base_node and \
            self._group_by == other._group_by and \
            self._order_by == other._order_by and \
            self._variables == other._variables

    @classmethod
    def from_table(
            cls,
            engine: Engine,
            table_name: str,
            index: List[str],
            all_dtypes: Optional[Mapping[str, StructuredDtype]] = None,
    ) -> 'DataFrame':
        """
        Instantiate a new DataFrame based on the content of an existing table in the database.

        If all_dtypes is not specified, the column dtypes are queried from the database's information
        schema.

        :param engine: a sqlalchemy engine for the database.
        :param table_name: the table name that contains the data to instantiate as DataFrame.
            Can include project_id and dataset on BigQuery, e.g. 'project_id.dataset.table_name'.
        :param index: list of column names that make up the index. At least one column needs to be
            selected for the index.
        :param all_dtypes: Optional. Mapping from column name to dtype.
            Must contain all index and data columns.
            Must be in same order as the columns appear in the the sql-model.
        :returns: A DataFrame based on a sql table.

        .. note::
            If all_dtypes is not set, then this will query the database.
        """
        if all_dtypes is not None:
            dtypes = all_dtypes
        else:
            dtypes = get_dtypes_from_table(
                engine=engine,
                table_name=table_name,
            )

        # We generate sql of the form (with quote characters depending on the database):
        # 'SELECT "column_1", ... , "column_N" FROM "table_name"'
        sql_params = {'table_name': quote_identifier(engine.dialect, table_name)}
        # use placeholders for columns in order to avoid conflicts when extracting spec references
        column_stmt = ','.join(f'{{col_{col_index}}}' for col_index in range(len(dtypes)))
        column_placeholders = {
            f'col_{col_index}': quote_identifier(engine.dialect, col_name)
            for col_index, col_name in enumerate(dtypes.keys())
        }
        sql_params.update(column_placeholders)

        sql = f'SELECT {column_stmt} FROM {{table_name}}'
        model_builder = CustomSqlModelBuilder(sql=sql, name='from_table')
        sql_model = model_builder(**sql_params)

        return cls._from_node(
            engine=engine,
            model=sql_model,
            index=index,
            all_dtypes=dtypes
        )

    @classmethod
    def from_model(
            cls,
            engine: Engine,
            model: SqlModel,
            index: List[str],
            all_dtypes: Optional[Mapping[str, StructuredDtype]] = None
    ) -> 'DataFrame':
        """
        Instantiate a new DataFrame based on the result of the query defined in `model`.

        If all_dtypes is not specified, then a transaction scoped temporary table will be created with
        0 result rows from the model. The meta data of this table will be used to deduce the dtypes.

        :param engine: a sqlalchemy engine for the database.
        :param model: an SqlModel that specifies the queries to instantiate as DataFrame.
        :param index: list of column names that make up the index. At least one column needs to be
            selected for the index.
        :param all_dtypes: Optional. Mapping from column name to dtype.
            Must contain all index and data columns.
            Must be in same order as the columns appear in the the sql-model.
        :returns: A DataFrame based on an SqlModel

        .. note::
            If all_dtypes is not set, then this will query the database and create and remove a temporary
            table.
        """
        if all_dtypes is not None:
            dtypes = all_dtypes
        else:
            dtypes = get_dtypes_from_model(engine=engine, node=model)
        return cls._from_node(
            engine=engine,
            model=model,
            index=index,
            all_dtypes=dtypes
        )

    @classmethod
    def _from_node(
            cls,
            engine,
            model: SqlModel,
            index: List[str],
            all_dtypes: Mapping[str, StructuredDtype]
    ) -> 'DataFrame':
        """
        INTERNAL: Instantiate a new DataFrame based on the result of the query defined in `model`.
        :param engine: an sqlalchemy engine for the database.
        :param model: an SqlModel that specifies the queries to instantiate as DataFrame.
        :param index: list of column names that make up the index. At least one column needs to be
            selected for the index.
        :param all_dtypes: Dictionary mapping column name to dtype.
            Must contain all index and data columns.
            Must be in same order as the columns appear in the the sql-model.
        :returns: A DataFrame based on an SqlModel

        """
        missing_index_keys = {k for k in index if k not in all_dtypes}
        if missing_index_keys:
            raise ValueError(f'Specified index keys ({missing_index_keys} not found in'
                             f' all_dtypes: {all_dtypes.keys()}')

        index_dtypes = {k: all_dtypes[k] for k in index}
        series_dtypes = {k: all_dtypes[k] for k in all_dtypes.keys() if k not in index}

        bach_model = BachSqlModel.from_sql_model(
            sql_model=model,
            column_expressions={c: Expression.column_reference(c) for c in all_dtypes.keys()},
        )

        from bach.savepoints import Savepoints
        df = cls.get_instance(
            engine=engine,
            base_node=bach_model,
            index_dtypes=index_dtypes,
            dtypes=series_dtypes,
            group_by=None,
            order_by=[],
            savepoints=Savepoints(),
            variables={}
        )
        if not df.is_materialized:
            # This happens when the columns in the model are in a different order than the columns in the
            # dataframe.
            df = df.materialize(node_name='column_reorder')
        return df

    @classmethod
    def from_pandas(
            cls,
            engine: Engine,
            df: pandas.DataFrame,
            convert_objects: bool,
            name: str = 'loaded_data',
            materialization: str = 'cte',
            *,
            if_exists: str = 'fail'
    ) -> 'DataFrame':
        """
        Instantiate a new DataFrame based on the content of a Pandas DataFrame.

        The index of the Pandas DataFrame is set to the index of the DataFrame. Only single level index is
        supported. Supported dtypes are 'int32', 'int64', 'float64', 'string', 'datetime64[ns]', 'bool'. If
        convert_objects is set to True, other columns are converted to supported data types if possible.

        How the data is loaded depends on the chosen materialization:

        1. 'table': This will first write the data to a database table using pandas
           :py:meth:`pandas.DataFrame.to_sql` method.
        2. 'cte': The data will be represented using a common table expression of the form
           ``select * from values`` in future queries.

        The 'table' method requires database write access. The 'cte' method is side-effect free and doesn't
        interact with the database at all. However the 'cte' method is only suitable for small quantities
        of data. For anything over a dozen kilobytes of data it is recommended to store the data in a table
        in the database first (e.g. by specifying 'table').

        There are some small differences between how the different materializations handle NaN values. e.g.
        'cte' does not support those for non-numeric columns, whereas 'table' converts them to 'NULL'.

        :param engine: an sqlalchemy engine for the database.
        :param df: Pandas DataFrame to instantiate as DataFrame.
        :param convert_objects: If True, the data in the columns with dtypes not in the list of supported
            dtypes are checked they contain supported data types. 'Object' columns that contain strings are
            converted to the 'string' dtype and loaded accordingly. Other types can only be loaded if
            materialization is 'cte' and the type is supported as Bach Series.
        :param name:
            * For 'table' materialization: name of the table that Pandas will write the data to.
            * For 'cte' materialization: name of the node in the underlying SqlModel graph.
        :param materialization: {'cte', 'table'}. How to materialize the data.
        :param if_exists: {'fail', 'replace', 'append'}. Only applies to `materialization='table'`
            How to behave if the table already exists:

            * fail: Raise a ValueError.
            * replace: Drop the table before inserting new values.
            * append: Insert new values to the existing table.
        :returns: A DataFrame based on a pandas DataFrame

        .. warning::
            This method is only suited for small quantities of data.
        """
        # todo link to pandas does not link
        # todo materialzation is 'cte' by default, add warning for large dataframe?
        from bach.from_pandas import from_pandas
        return from_pandas(
            engine=engine,
            df=df,
            convert_objects=convert_objects,
            materialization=materialization,
            name=name,
            if_exists=if_exists
        )

    @classmethod
    def get_instance(
        cls,
        engine,
        base_node: BachSqlModel,
        index_dtypes: Mapping[str, StructuredDtype],
        dtypes: Mapping[str, StructuredDtype],
        group_by: Optional['GroupBy'],
        order_by: List[SortColumn],
        savepoints: 'Savepoints',
        variables: Dict['DtypeNamePair', Hashable]
    ) -> 'DataFrame':
        """
        INTERNAL: Get an instance with the right series instantiated based on the dtypes array.

        This assumes that base_node has a column for all names in index_dtypes and dtypes.
        If single_value is True, SingleValueExpression is used as the class for the series expressions
        """
        base_params = {
            'engine': engine,
            'base_node': base_node,
            'group_by': group_by,
            'order_by': [],
        }
        index: Dict[str, Series] = {
            name: get_series_type_from_dtype(dtype).get_class_instance(
                index={},  # Empty index for index series
                name=name,
                expression=Expression.column_reference(name),
                instance_dtype=dtype,
                **base_params
            )
            for name, dtype in index_dtypes.items()
        }

        series: Dict[str, Series] = {
            name: get_series_type_from_dtype(dtype).get_class_instance(
                index=index,
                name=name,
                expression=Expression.column_reference(name),
                instance_dtype=dtype,
                **base_params
            )
            for name, dtype in dtypes.items()
        }

        return cls(
            engine=engine,
            base_node=base_node,
            index=index,
            series=series,
            group_by=group_by,
            order_by=order_by,
            savepoints=savepoints,
            variables=variables
        )

    def copy_override(
        self,
        engine: Optional[Engine] = None,
        base_node: Optional[BachSqlModel] = None,
        index: Optional[Mapping[str, 'Series']] = None,
        series: Optional[Mapping[str, 'Series']] = None,
        group_by: Optional[Union['GroupBy', NotSet]] = not_set,
        order_by: Optional[List[SortColumn]] = None,
        variables: Optional[Dict[DtypeNamePair, Hashable]] = None,
        index_dtypes: Optional[Mapping[str, StructuredDtype]] = None,
        series_dtypes: Optional[Mapping[str, StructuredDtype]] = None,
        single_value: bool = False,
        savepoints: Optional['Savepoints'] = None,
        **kwargs
    ) -> 'DataFrame':
        """
        INTERNAL

        Create a copy of self, with the given arguments overridden

        There are three special parameters: index_dtypes, series_dtypes and single_value. These are used to
        create new index and data series iff index and/or series are not given. `single_value` determines
        whether the Expressions for those newly created series should be SingleValueExpressions or not.
        All other arguments are passed through to `__init__`, filled with current instance values if None is
        given in the parameters.
        """

        if index_dtypes and index:
            raise ValueError("Can not set both index and index_dtypes")

        if series_dtypes and series:
            raise ValueError("Can not set both series and series_dtypes")

        args = {
            'engine': engine if engine is not None else self.engine,
            'base_node': base_node if base_node is not None else self._base_node,
            'index': index if index is not None else self._index,
            'series': series if series is not None else self._data,
            'group_by': self._group_by if group_by is not_set else group_by,
            'order_by': order_by if order_by is not None else self._order_by,
            'savepoints': savepoints if savepoints is not None else self.savepoints,
            'variables': variables if variables is not None else self.variables
        }

        expression_class = SingleValueExpression if single_value else Expression

        if index_dtypes:
            new_index: Dict[str, Series] = {}
            for name, dtype in index_dtypes.items():
                index_type = get_series_type_from_dtype(dtype)
                new_index[name] = index_type(
                    engine=args['engine'],
                    base_node=args['base_node'],
                    index={},  # Empty index for index series
                    name=name,
                    expression=expression_class.column_reference(name),
                    group_by=args['group_by'],
                    order_by=[],
                    instance_dtype=dtype
                )
            args['index'] = new_index

        if series_dtypes:
            from bach.series import SeriesAbstractMultiLevel
            new_series: Dict[str, Series] = {}
            for name, dtype in series_dtypes.items():
                series_type = get_series_type_from_dtype(dtype)
                extra_params = {}

                if issubclass(series_type, SeriesAbstractMultiLevel):
                    if name not in self._data:
                        raise Exception(
                            f'cannot instantiate {series_type.__name__} class without level information.'
                        )
                    multi_level_series = cast(SeriesAbstractMultiLevel, self.all_series[name])
                    extra_params.update(
                        {
                            lvl_name: lvl.copy_override(
                                expression=expression_class.column_reference(f'_{name}_{lvl_name}')
                            )
                            for lvl_name, lvl in multi_level_series.levels.items()
                        }
                    )

                new_series[name] = series_type.get_class_instance(
                    engine=args['engine'],
                    base_node=args['base_node'],
                    index=args['index'],  # Empty index for index series
                    name=name,
                    expression=expression_class.column_reference(name),
                    group_by=args['group_by'],
                    order_by=[],
                    instance_dtype=dtype,
                    **extra_params
                )
            args['series'] = new_series

        return self.__class__(**args, **kwargs)

    def copy_override_base_node(self, base_node: BachSqlModel) -> 'DataFrame':
        """
        INTERNAL

        Create a copy of self, with the base_node overridden in both the returned DataFrame and the Series
        that are part of that DataFrame. If self.group_by is not None, then it's base_node is updated as
        well.
        This is different from :py:meth:`copy_override()`, which when provided with a new base_node only
        overrides the base_node of the DataFrame and not of the Series that make up the DataFrame nor of
        the GroupBy.
        """
        index = {name: series.copy_override(base_node=base_node) for name, series in self.index.items()}

        group_by = self.group_by
        if group_by is not None:
            group_by = group_by.copy_override_base_node(base_node=base_node)

        series = {
            name: series.copy_override(
                base_node=base_node,
                group_by=group_by,
                index=index,
                order_by=[]
            )
            for name, series in self.data.items()
        }

        return self.copy_override(base_node=base_node, index=index, series=series, group_by=group_by)

    def copy(self):
        """
        Return a copy of this DataFrame.

        As this dataframe only represents data in the backing SQL store, and does not contain any data,
        this is a metadata copy only, no actual data is duplicated and changes to the underlying data
        will represented in both copy and original.
        Changes to data, index, sorting, grouping etc. on the copy will not affect the original.
        The savepoints on the other hand will be shared by the original and the copy.

        If you want to create a snapshot of the data, have a look at :py:meth:`database_create_table()`.

        Calling `copy(df)` will invoke this copy function, i.e. `copy(df)` is implemented as df.copy().

        :returns: A copy of the DataFrame.
        """
        return self.copy_override()

    def __copy__(self):
        return self.copy()

    def _update_self_from_df(self, df: 'DataFrame') -> 'DataFrame':
        """
        INTERNAL: Modify self by copying all properties of 'df' to self. Returns self.
        """
        self._engine = df.engine
        self._base_node = df.base_node
        self._index = df.index
        self._data = df.data
        self._group_by = df.group_by
        self._order_by = df.order_by
        self._savepoints = df.savepoints
        self._variables = df.variables
        return self

    def materialize(
        self,
        node_name='manual_materialize',
        inplace=False,
        limit: Any = None,
        distinct: bool = False,
        materialization: Union[Materialization, str] = Materialization.CTE
    ) -> 'DataFrame':
        """
        Create a copy of this DataFrame with as base_node the current DataFrame's state.

        This effectively adds a node to the underlying SqlModel graph. Generally adding nodes increases
        the size of the generated SQL query. But this can be useful if the current DataFrame contains
        expressions that you want to evaluate before further expressions are build on top of them. This might
        make sense for very large expressions, or for non-deterministic expressions (e.g. see
        :py:meth:`SeriesUuid.random()`). Additionally, materializing as a temporary table can
        improve performance in some instances.

        Note this function does NOT query the database or materializes any data in the database. It merely
        changes the underlying SqlModel graph, which gets executed by data transfer functions (e.g.
        :meth:`to_pandas()`)

        TODO: a known problem is that DataFrames with 'json_postgres' columns cannot be fully materialized.

        :param node_name: The name of the node that's going to be created
        :param inplace: Perform operation on self if ``inplace=True``, or create a copy.
        :param limit: The limit (slice, int) to apply.
        :param distinct: Apply distinct statement if ``distinct=True``
        :param materialization: Set the materialization of the SqlModel in the graph. Only
            Materialization.CTE / 'cte' and Materialization.TEMP_TABLE / 'temp_table' are supported.
        :returns: DataFrame with the current DataFrame's state as base_node

        .. note::
            Calling materialize() resets the order of the dataframe. Call :py:meth:`sort_values()` again on
            the result if order is important.
        """
        index_dtypes = {k: v.instance_dtype for k, v in self.index.items()}
        series_dtypes = {k: v.instance_dtype for k, v in self.data.items()}
        node = self.get_current_node(name=node_name, limit=limit, distinct=distinct)
        materialization = Materialization.normalize(materialization)
        assert materialization in (Materialization.CTE, Materialization.TEMP_TABLE)
        node = node.copy_set_materialization(materialization=materialization)

        df = self.get_instance(
            engine=self.engine,
            base_node=node,
            index_dtypes=index_dtypes,
            dtypes=series_dtypes,
            group_by=None,
            order_by=[],
            savepoints=self.savepoints,
            variables=self.variables
        )

        if not inplace:
            return df
        return self._update_self_from_df(df)

    def set_savepoint(self, name: str, materialization: Union[Materialization, str] = Materialization.CTE):
        """
        Set the current state as a savepoint in `self.savepoints`.

        :param save_points: Savepoints object that's responsible for tracking all savepoints.
        :param name: Name for the savepoint. This will be the name of the table or view if that's set as
            materialization. Must be unique both within the Savepoints and within the base_node.
        :param materialization: Optional materialization of the savepoint in the database. This doesn't do
            anything unless self.savepoints.write_to_db() gets called and the savepoints are actually
            materialized into the database.
        """
        if not self.is_materialized:
            self.materialize(node_name=name, inplace=True, limit=None)
        materialization = Materialization.normalize(materialization)
        self.savepoints.add_savepoint(name=name, df=self, materialization=materialization)
        return self

    def get_sample(self,
                   table_name: str,
                   filter: 'SeriesBoolean' = None,
                   sample_percentage: int = None,
                   *,
                   overwrite: bool = False,
                   seed: int = None) -> 'DataFrame':
        """
        Returns a DataFrame whose data is a sample of the current DataFrame object.

        For the sample Dataframe to be created, all data is queried once and a persistent table is created to
        store the sample data used for the sampled DataFrame.

        Use :py:meth:`get_unsampled` to switch back to the unsampled data later on. This returns a new
        DataFrame with all operations that have been done on the sample, applied to that DataFrame.

        Will materialize the DataFrame if it is not in a materialized state.

        If `seed` is set (Postgres only), this will create a temporary table from which the sample will be
        queried using the `tablesample bernoulli` sql construction.

        :param table_name: the name of the underlying sql table that is created to store the sampled data.
            Can include project_id and dataset on BigQuery, e.g. 'project_id.dataset.table_name'
        :param filter: a filter to apply to the dataframe before creating the sample. If a filter is applied,
            sample_percentage is ignored and thus the bernoulli sample creation is skipped.
        :param sample_percentage: the approximate size of the sample as a proportion of all rows.
            Between 0-100.
        :param overwrite: if True, the sample data is written to table_name, even if that table already
            exists.
        :param seed: optional seed number used to generate the sample. Only supported for Postgres.
        :raises Exception: If overwrite=False and the table already exists. The exact exception depends on
            the underlying database.
        :returns: a sampled DataFrame of the current DataFrame.

        .. warning::
            With `overwrite=True`, if a table already exist with the given name, then that table will
            be dropped and all data lost!
        .. note::
            This function queries the database.
        .. note::
            This function writes to the database.
        .. note::
            All data in the DataFrame to be sampled is queried to create the sample.
        """
        # todo if_exists and overwrite are two different syntax for the same thing. should we align?
        from bach.sample import get_sample
        return get_sample(
            df=self,
            table_name=table_name,
            filter=filter,
            sample_percentage=sample_percentage,
            overwrite=overwrite,
            seed=seed
        )

    def get_unsampled(self) -> 'DataFrame':
        """
        Return a copy of the current sampled DataFrame, that undoes calling :py:meth:`get_sample()` earlier.

        All other operations that have been done on the sample DataFrame will be applied on the DataFrame
        that is returned. The returned DataFrame's data will look as if :py:meth:`get_sample()` was never
        called, but the state of the DataFrame could be slightly different since :py:meth:`get_sample()`
        might have called :py:meth:`materialize()`.

        This does not remove the table that was written to the database by :py:meth:`get_sample()`, the new
        DataFrame just does not query that table anymore.

        Will raise an error if the current DataFrame is not sample data of another DataFrame, i.e.
        :py:meth:`get_sample` has not been called.

        :returns: An unsampled copy of the current sampled DataFrame.
        """
        from bach.sample import get_unsampled
        return get_unsampled(df=self)

    def database_create_table(self, table_name: str, *, if_exists: str = 'fail') -> 'DataFrame':
        """
        Write the current state of the DataFrame to a database table.

        The DataFrame that's returned will query from the written table for any further operations.

        :param table_name: Name of the table to write to. Can include project_id and dataset
            on BigQuery, e.g. 'project_id.dataset.table_name'
        :param if_exists: {'fail', 'replace'}. How to behave if the table already exists:

            * fail: Raise an Exception.
            * replace: Drop the table before inserting new values. All data in that table will be lost! Make \
            sure that `table_name` does not contain any valuable information. Additionally, make sure \
            that it is not a source table of this DataFrame.

        :raises Exception: If if_exists='fail'' and the table already exists. The exact exception depends on
            the underlying database.
        :return: New DataFrame; the base_node consists of a query on the newly created table.

        .. warning::
            With `if_exists='replace'`, if a table already exist with the given name, then that table will
            be dropped and all data lost!
        .. note::
            This function queries the database.
        .. note::
            This function writes to the database.
        """
        if if_exists not in {'fail', 'replace'}:
            raise ValueError(f'Value of if_exists ({if_exists}) must be either "fail" or "replace"')
        dialect = self.engine.dialect
        model = self.get_current_node(name='database_create_table')
        model = model.copy_set_materialization(Materialization.TABLE)
        model = model.copy_set_materialization_name(materialization_name=table_name)

        placeholder_values = get_variable_values_sql(dialect=dialect, variable_values=self.variables)
        model = update_placeholders_in_graph(start_node=model, placeholder_values=placeholder_values)

        sql = to_sql(dialect=dialect, model=model)
        with self.engine.connect() as conn:
            if if_exists == 'replace':
                sql = f'DROP TABLE IF EXISTS {quote_identifier(dialect, table_name)}; {sql}'

            sql = escape_parameter_characters(conn, sql)
            conn.execute(sql)

        all_dtypes = {**self.index_dtypes, **self.dtypes}
        return self.from_table(
            engine=self.engine,
            table_name=table_name,
            index=self.index_columns,
            all_dtypes=all_dtypes
        )

    @overload
    def __getitem__(self, key: str) -> 'Series':
        ...

    @overload
    def __getitem__(self, key: Union[List[str], Set[str], slice, 'SeriesBoolean']) -> 'DataFrame':
        ...

    def __getitem__(self, key):
        """
        For usage see general introduction DataFrame class.
        """
        from bach.series import SeriesBoolean

        if isinstance(key, str):
            return self.data[key]
        if isinstance(key, (set, list)):
            key_set = set(key)
            if not key_set.issubset(set(self.data_columns)):
                raise KeyError(f"Keys {key_set.difference(set(self.data_columns))} not in data_columns")

            if isinstance(key, set):
                selected_data = {col: data for col, data in self.data.items() if col in key_set}
            else:
                # should change order of columns in select
                selected_data = {col: self.data[col] for col in key}

            return self.copy_override(series=selected_data)

        if isinstance(key, (SeriesBoolean, slice, int)):
            if isinstance(key, int):
                raise NotImplementedError("index key lookups not supported, use slices instead.")
            if isinstance(key, slice):
                node = self.get_current_node(name='getitem_slice', limit=key)
                single_value = (
                    # This is our best guess, there can always be zero results, but at least we tried.
                    # Negative slices are not supported, Exceptions was raised in get_current_node()
                    (key.stop is not None and key.start is None and key.stop == 1)
                    or
                    (key.start is not None and key.stop is not None and (key.stop - key.start) == 1)
                )
            else:
                single_value = False  # there is no way for us to know. User has to slice the result first

                if key.base_node != self.base_node:
                    raise ValueError('Cannot apply Boolean series with a different base_node to DataFrame. '
                                     'Hint: make sure the Boolean series is derived from this DataFrame and '
                                     'that is has the same group by or use df.merge(series) to merge the '
                                     'series with the df first, and then create a new Boolean series on the '
                                     'resulting merged data.')

                # window functions do not have group_by set, but they can't be used without materialization
                if key.expression.has_windowed_aggregate_function:
                    raise ValueError('Cannot apply a Boolean series containing a window function to '
                                     'DataFrame. Hint: materialize() the DataFrame before creating the '
                                     'Boolean series')

                # If the key has no group_by but the df has, this is a filter before aggregation. This is
                # supported but it can change the aggregated results.
                # (A common case is a filter on the columns in the group_by e.g. the index of this df.)
                # We might come back to this when we keep conditions (where/having) as state.

                # We don't support using aggregated series to filter on a non-aggregated df though:
                if key.group_by and not self._group_by:
                    raise ValueError('Can not apply aggregated BooleanSeries to a non-grouped df.'
                                     'Please merge() the selector df with this df first.')

                # If a group_by is set on both, they have to match.
                if key.group_by and key.group_by != self._group_by:
                    raise ValueError('Can not apply aggregated BooleanSeries with non matching group_by.'
                                     'Please merge() the selector df with thisdf first.')

                if key.group_by is not None and key.expression.has_aggregate_function:
                    # Create a having-condition if the key is aggregated
                    node = self.get_current_node(
                        name='getitem_having_boolean',
                        having_clause=Expression.construct("having {}", key.expression))
                else:
                    # A normal where-condition will do
                    node = self.get_current_node(
                        name='getitem_where_boolean',
                        where_clause=Expression.construct("where {}", key.expression))

            return self.copy_override(
                base_node=node,
                group_by=None,
                index_dtypes={name: series.instance_dtype for name, series in self.index.items()},
                series_dtypes={name: series.instance_dtype for name, series in self.data.items()},
                single_value=single_value
            )
        raise NotImplementedError(f"Only str, (set|list)[str], slice or SeriesBoolean are supported, "
                                  f"but got {type(key)}")

    def __getattr__(self, attr):
        """
        After regular attribute access, try looking up the name. This allows simpler access to columns for
        interactive use.
        """
        return self._data[attr]

    def __setitem__(self,
                    key: Union[str, List[str]],
                    value: Union[AllSupportedLiteralTypes, 'Series', pandas.Series]):
        """
        For usage see general introduction DataFrame class.
        """
        from bach.series import Series, value_to_series, SeriesAbstractMultiLevel
        if isinstance(key, str):
            if key in self.index:
                # Cannot set an index column, and cannot have a column name both in self.index and self.data
                raise ValueError(f'Column name "{key}" already exists as index.')

            if any(
                key in [level.name for level in series.levels.values()]
                for series in self.all_series.values() if isinstance(series, SeriesAbstractMultiLevel)
            ):
                raise ValueError(f'Column name "{key}" already exists as a level in a series multilevel')

            if isinstance(value, DataFrame):
                raise ValueError("Can't set a DataFrame as a single column")
            if isinstance(value, pandas.Series):
                df = pandas.DataFrame(value)
                df.columns = [key]
                bt = DataFrame.from_pandas(self.engine,
                                           df,
                                           convert_objects=True)
                value = bt[key]
            if not isinstance(value, Series):
                series = value_to_series(base=self, value=value, name=key)
                self._data[key] = series
            else:
                if value.base_node == self.base_node and self._group_by == value.group_by:
                    self._data[key] = value.copy_override(name=key, index=self._index)
                elif value.expression.is_constant:
                    self._data[key] = value.copy_override(
                        name=key, index=self._index, group_by=self._group_by,
                    )
                elif value.expression.is_independent_subquery:
                    self._data[key] = value.copy_override(
                        name=key, index=self._index, group_by=self._group_by,
                    )
                elif value.expression.is_single_value:
                    self._data[key] = Series.as_independent_subquery(value).copy_override(
                        name=key, index=self._index, group_by=self._group_by,
                    )
                else:
                    if value.group_by and not value.expression.has_aggregate_function:
                        raise ValueError('Setting a grouped Series to a DataFrame is only supported if '
                                         'the Series is aggregated.')
                    if (
                        self.group_by
                        and not all(_s.expression.has_aggregate_function for _s in self.data.values())
                    ):
                        raise ValueError('Setting new columns to grouped DataFrame is only supported if '
                                         'the DataFrame has aggregated columns.')
                    self.__set_item_with_merge(key=key, value=value)

        elif isinstance(key, list):
            if len(key) == 0:
                return
            if len(key) == 1:
                return self.__setitem__(key[0], value)
            # len(key) > 1
            if not isinstance(value, DataFrame):
                raise ValueError(f'Assigned value should be a bach.DateFrame, provided: {type(value)}')
            if len(value.data_columns) != len(key):
                raise ValueError(f'Number of columns in key and value should match. '
                                 f'Key: {len(key)}, value: {len(value.data_columns)}')
            series_list = [value.data[col_name] for col_name in value.data_columns]
            for i, sub_key in enumerate(key):
                self.__setitem__(sub_key, series_list[i])
        else:
            raise ValueError(f'Key should be either a string or a list of strings, value: {key}')

    def __set_item_with_merge(self, key: str, value: 'Series'):
        """"
        Internal method used by __setitem__ to set a series using a merge on index. Modifies the DataFrame
        with the added column. The DataFrames index name is the same as the original DataFrame's.

        :param key: name of the column to set.
        :param value: Series that is set.
        """

        if not (len(value.index) == 1 and len(self.index) == 1):
            raise ValueError(
                'setting with different base nodes only supported for one level index'
            )

        from bach.partitioning import GroupBy
        index_name = self.index_columns[0]
        value_index_name = list(value.index.keys())[0]
        if self.index[index_name].dtype != value.index[value_index_name].dtype:
            raise ValueError('dtypes of indexes should be the same')

        # align index names, this way we have all matched indexes in a single series after merge
        # TODO: replace with value.rename(index={value_index_name: index_name})
        #  when index renaming is supported
        aligned_index = {index_name: value.index[value_index_name].copy_override(name=index_name)}
        other = value.copy_override(
            index=aligned_index,
            name=key,
            group_by=GroupBy(list(aligned_index.values())) if value.group_by else None,
        )

        df = self.merge(
            other,
            left_index=True,
            right_index=True,
            how='left',
            suffixes=('', '__remove'),
        )

        # remove conflicts in case self already has a value for series key
        if key in self.data_columns:
            df[key] = df[key + '__remove']
            df = df.drop(columns=[key + '__remove'])
        self._update_self_from_df(df)

    def rename(
        self,
        mapper: Union[Dict[str, str], Callable[[str], str]] = None,
        index: Union[Dict[str, str], Callable[[str], str]] = None,
        columns: Union[Dict[str, str], Callable[[str], str]] = None,
        axis: int = 0,
        level: int = None,
        errors: str = 'ignore',
    ) -> 'DataFrame':
        """
        Rename columns.

        The interface is similar to Panda's :py:meth:`pandas.DataFrame.rename`. However we don't support
        renaming indexes, so recommended usage is ``rename(columns=...)``.

        :param mapper: dict to apply to that axis' values. Use mapper and axis to specify the axis to target
            with mapper. Currently mapper is only supported with ``axis=1``, which is similar to using
            columns.
        :param index: not supported.
        :param columns: dict str:str to rename columns, or a function that takes column names as an argument
            and returns the new one. The new column names must not clash with other column names in either
            `self.`:py:attr:`data` or `self.`:py:attr:`index`, after renaming is complete.
        :param axis: ``axis=1`` is supported, rest is not.
        :param level: not supported
        :param errors: Either 'ignore' or 'raise'. When set to 'ignore' KeyErrors about non-existing
            column names in `columns` or `mapper` are ignored. Errors thrown in the mapper function or
            about invalid target column names are not suppressed.
        :returns: DataFrame with the renamed axis labels.

        .. note::
            The copy parameter is not supported since it makes very little sense for db backed series.
        """
        # todo should we support arguments of unsupported functionality?
        # todo note is not visible in docstring do we want that?
        if level is not None or \
                index is not None or \
                (mapper is not None and axis == 0):
            raise NotImplementedError("index renames not supported")

        if mapper is not None:
            columns = mapper

        df = self.copy_override()

        if callable(columns):
            columns = {source: columns(source) for source in df.data_columns}

        if not isinstance(columns, dict):
            raise TypeError(f'unsupported argument type for columns or mappers: {type(columns)}')

        non_existing_columns = set(columns.keys()) - set(df.data.keys())
        if errors == 'raise' and non_existing_columns:
            raise KeyError(f'No such column(s): {non_existing_columns}')

        from bach.series import Series
        new_data: Dict[str, 'Series'] = {}
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

    def reset_index(
        self,
        level: Optional[Union[str, Sequence[str]]] = None,
        drop: bool = False,
    ) -> 'DataFrame':
        """
        Drops the current index.

        With reset_index, all indexes are removed from the DataFrame, so that the DataFrame does not have any
        index Series. A new index can be set with :py:meth:`set_index`.

        :param level: Removes given levels from index. Removes all levels by default
        :param drop: if False, the dropped index is added to the data columns of the DataFrame. If True it
            is removed.
        :returns: DataFrame with the index dropped.
        """
        df = self.copy()
        if self._group_by:
            df = df.materialize(node_name='reset_index')

        new_index = {}
        series = df._data if drop else df.all_series
        if level is not None:
            series = df._data
            levels_to_remove = [level] if isinstance(level, str) else level

            for lvl in levels_to_remove:
                if lvl not in df._index:
                    raise ValueError(f'\'{lvl}\' level not found in index')

                if not drop:
                    series[lvl] = df.index[lvl]

            new_index = {idx: series for idx, series in df.index.items() if idx not in levels_to_remove}

        df._data = {n: s.copy_override(index=new_index, order_by=[]) for n, s in series.items()}
        df._index = new_index
        return df

    def set_index(
        self,
        keys: Union[str, 'Series', Sequence[Union[str, 'Series']]],
        drop: bool = True,
        append: bool = False,
    ) -> 'DataFrame':
        """
        Set this dataframe's index to the the index given in keys

        :param keys: the keys of the new index. Can be a column name str, a Series, or a list of those. If
            Series are passed, they should have the same base node as the DataFrame they are set on.
        :param drop: delete columns to be used as the new index.
        :param append: whether to append to the existing index or replace.
        :returns: a DataFrame with the new index.
        """
        from bach.series import Series

        df = self.copy()
        if self._group_by:
            df = df.materialize(node_name='groupby_setindex')

        # build the new index, appending if necessary
        new_index = {} if not append else copy(df._index)
        for k in (keys if isinstance(keys, list) else [keys]):
            idx_series: Series
            if isinstance(k, Series):
                if k.base_node != df.base_node or k.group_by != df.group_by:
                    raise ValueError('index series should have same base_node and group_by as df')
                idx_series = k
            else:
                if k not in df.all_series:
                    raise ValueError(f'series \'{k}\' not found')
                idx_series = df.all_series[k]

            new_index[idx_series.name] = idx_series.copy_override(index={}, order_by=[])

            if not drop and idx_series.name not in df._index and idx_series.name in df._data:
                raise ValueError('When adding existing series to the index, drop must be True'
                                 ' because duplicate column names are not supported.')

        new_series = {
            n: s.copy_override(index=new_index, order_by=[]) for n, s in df._data.items()
            if n not in new_index
        }

        df._index = new_index
        df._data = new_series
        return df

    def __delitem__(self, key: str):
        """
        Deletes columns from the DataFrame.
        """
        if isinstance(key, str):
            del (self._data[key])
            return
        else:
            raise TypeError(f'Unsupported type {type(key)}')

    def drop(
        self,
        labels: List[str] = None,
        index: List[str] = None,
        columns: List[str] = None,
        level: int = None,
        errors: str = 'raise',
    ) -> 'DataFrame':
        """
        Drop columns from the DataFrame

        :param labels: not supported
        :param index: not supported
        :param columns: the list of columns to drop.
        :param level: not supported
        :param errors: 'raise' or 'ignore' missing key errors.
        :returns: DataFrame without the removed columns.

        """
        if labels or index is not None:
            # TODO we could do this using a boolean __series__
            raise NotImplementedError('dropping labels from index not supported.')

        if level is not None:
            raise NotImplementedError('dropping index levels not supported.')

        if columns is None:
            raise ValueError("columns needs to be a list of strings.")

        df = self.copy_override()

        try:
            for key in columns:
                del (df[key])
        except Exception as e:
            if errors == "raise":
                raise e

        return df

    def astype(self, dtype: Union[str, Dict[str, str]]) -> 'DataFrame':
        """
        Cast all or some of the data columns to a certain dtype.

        Only data columns can be cast, index columns cannot be cast.

        This does not modify the current DataFrame, instead it returns a new DataFrame.

        :param dtype: either:

            * A single str, in which case all data columns are cast to this dtype.
            * A dictionary mapping column labels to dtype.
        :returns: New DataFrame with the specified column(s) cast to the specified dtype
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

    # Some typing help required here.
    _GroupBySingleType = Union[str, 'Series']
    # TODO exclude from docs

    def _partition_by_series(self,
                             by: Union[_GroupBySingleType,
                                       Union[List[_GroupBySingleType], Tuple[_GroupBySingleType, ...]],
                                       None]) -> List['Series']:
        """
        Helper method to check and compile a partitioning list
        """
        from bach.series import Series
        group_by_columns: List['Series'] = []
        if isinstance(by, str):
            group_by_columns.append(self.all_series[by])
        elif isinstance(by, Series):
            group_by_columns.append(by)
        elif isinstance(by, list):
            for by_item in by:
                if isinstance(by_item, str):
                    group_by_columns.append(self.all_series[by_item])
                if isinstance(by_item, Series):
                    group_by_columns.append(by_item)
        elif by is None:
            pass
        else:
            raise ValueError(f'Value of "by" should be either None, a string, or a Series.')

        return group_by_columns

    @classmethod
    def _groupby_to_frame(cls, df: 'DataFrame', group_by: 'GroupBy'):
        """
        Given a group_by, and a df create a new DataFrame that has all the right stuff set.
        It will not materialize, just prepared for more operations
        """
        new_series = {s.name: s.copy_override(group_by=group_by, index=group_by.index, order_by=[])
                      for n, s in df.data.items() if n not in group_by.index.keys()}
        return df.copy_override(
            index=group_by.index,
            series=new_series,
            group_by=group_by,
        )

    def groupby(
            self,
            by: Union[_GroupBySingleType,  # single series group_by
                      # for GroupingSets
                      Tuple[Union[_GroupBySingleType, Tuple[_GroupBySingleType, ...]], ...],
                      Sequence[Union[_GroupBySingleType,  # multi series
                                     List[_GroupBySingleType],  # for grouping lists
                                     Tuple[_GroupBySingleType, ...]]],  # for grouping lists
                      None] = None) -> 'DataFrame':
        """
        Group by any of the series currently in this DataDrame, both from index as well as data.

        :param by: The series to group by. Supported are:

            * a string containing a columnn name.
            * a series.
            * a list of strings or series. A normal group by will be created.
            * a list of (strings, series, lists). In this case a grouping list is created.
            * a tuple of (strings, series, lists). In this case a grouping set is created.
        :returns: a new DataFrame object with the :py:attr:`group_by` attribute set.

        .. note::
            If the dataframe is already grouped, we'll create a grouping list from the initial
            grouping combined with this one.
        """
        # todo the grouping set / list relevant?
        # todo format bullet points: text does not start on same line as parameter
        from bach.partitioning import GroupBy, GroupingList, GroupingSet

        df = self
        if df._group_by:
            # We need to materialize this node first, we can't stack aggregations (yet)
            df = df.materialize(node_name='nested_groupby')

        group_by: GroupBy
        if isinstance(by, tuple):
            if not is_postgres(self.engine):
                raise DatabaseNotSupportedException(
                    self.engine,
                    f'GroupingSets are not supported for this SQL dialect. Only grouping by one or more '
                    f'Series is supported. To use this functionality: specify a Series, a list of Series, a '
                    f'Series name, or a list of Series names. Dialect: {self.engine.name}')
            # by is a list containing at least one other list. We're creating a grouping set
            # aka "Yo dawg, I heard you like GroupBys, ..."
            group_by = GroupingSet(
                [GroupBy(group_by_columns=df._partition_by_series(b)) for b in by]
            )
            return DataFrame._groupby_to_frame(df, group_by)

        if isinstance(by, list) and len([b for b in by if isinstance(b, (tuple, list))]) > 0:
            if not is_postgres(self.engine):
                raise DatabaseNotSupportedException(
                    self.engine,
                    f'GroupingLists are not supported for this SQL dialect. Only grouping by one or more '
                    f'Series is supported. To use this functionality: specify a Series, a list of Series, a '
                    f'Series name, or a list of Series names. Dialect: {self.engine.name}')
            group_by = GroupingList(
                [GroupBy(group_by_columns=df._partition_by_series(b)) for b in by])
            return DataFrame._groupby_to_frame(df, group_by)

        # This is the normal group-by case
        by_mypy = cast(Union[str, 'Series',
                             List[DataFrame._GroupBySingleType], None], by)
        group_by = GroupBy(group_by_columns=df._partition_by_series(by_mypy))
        return DataFrame._groupby_to_frame(df, group_by)

    def window(self, **frame_args) -> 'DataFrame':
        """
        Create a window on the current dataframe grouping and its sorting.

        .. warning::
            This is an expert method. Use :py:meth:`rolling` or :py:meth:`expanding` if possible.

        see :py:class:`bach.partitioning.Window` for parameters.
        """
        # TODO Better argument typing, needs fancy import logic
        from bach.partitioning import Window
        index = list(self._group_by.index.values()) if self._group_by else []
        group_by = Window(group_by_columns=index,
                          order_by=self._order_by,
                          **frame_args)
        return DataFrame._groupby_to_frame(self, group_by)

    def cube(self,
             by: Union[str, 'Series', List[Union[str, 'Series']], None],
             ) -> 'DataFrame':
        """
        Group by and cube over the column(s) `by`.

        :param by: the series to group by and cube. Can be a column or index name str, a Series or a list
            of any of those. If Series are passed, they should have the same base node as the DataFrame.
        :returns: a new DataFrame object with the :py:attr:`group_by` attribute set.
        """
        from bach.partitioning import Cube
        index = self._partition_by_series(by)
        group_by = Cube(group_by_columns=index)
        return DataFrame._groupby_to_frame(self, group_by)

    def rollup(self,
               by: Union[str, 'Series', List[Union[str, 'Series']], None],
               ) -> 'DataFrame':
        """
        Group by and roll up over the column(s) `by`, replacing any current grouping.

        :param by: the series to group by and roll up. Can be a column or index name str, a Series or a list
            of any of those. If Series are passed, they should have the same base node as the DataFrame.
        :returns: a new DataFrame object with the :py:attr:`group_by` attribute set.
        """
        # todo update tests?
        from bach.partitioning import Rollup
        index = self._partition_by_series(by)
        group_by = Rollup(group_by_columns=index)
        return DataFrame._groupby_to_frame(self, group_by)

    def rolling(self, window: int,
                min_periods: int = None,
                center: bool = False,
                closed: str = 'right') -> 'DataFrame':
        """
        A rolling window of size 'window', by default right aligned.

        To use grouping as well, first call :py:meth:`group_by` on this frame and call rolling on the result.

        :param window: the window size.
        :param min_periods: the min amount of rows included in the window before an actual value is returned.
        :param center: center the result, or align the result on the right.
        :param closed: make the interval closed on the ‘right’, ‘left’, ‘both’ or ‘neither’ endpoints.
            Defaults to ‘right’, and the rest is currently unsupported.
        :returns: a new DataFrame object with the :py:attr:`group_by` attribute set with a
            :py:class:`bach.partitioning.Window`.

        .. note::
            The `win_type`, `axis` and `method` parameters as supported by pandas, are currently not
            implemented.
        """
        from bach.partitioning import WindowFrameBoundary, WindowFrameMode, Window

        if min_periods is None:
            min_periods = window

        if min_periods > window:
            raise ValueError(f'min_periods {min_periods} must be <= window {window}')

        if closed != 'right':
            raise NotImplementedError("Only closed=right is supported")

        mode = WindowFrameMode.ROWS
        end_value: Optional[int]
        if center:
            end_value = (window - 1) // 2
        else:
            end_value = 0

        start_boundary = WindowFrameBoundary.PRECEDING
        start_value = (window - 1) - end_value

        if end_value == 0:
            end_boundary = WindowFrameBoundary.CURRENT_ROW
            end_value = None
        else:
            end_boundary = WindowFrameBoundary.FOLLOWING

        index = list(self._group_by.index.values()) if self._group_by else []
        group_by = Window(group_by_columns=index,
                          order_by=self._order_by,
                          mode=mode,
                          start_boundary=start_boundary, start_value=start_value,
                          end_boundary=end_boundary, end_value=end_value,
                          min_values=min_periods)
        return DataFrame._groupby_to_frame(self, group_by)

    def expanding(self,
                  min_periods: int = 1,
                  center: bool = False,
                  ) -> 'DataFrame':
        """
        Create an expanding window starting with the first row in the group, with at least `min_period`
        observations. The result will be right-aligned in the window.

        To use grouping as well, first call :py:meth:`group_by` on this frame and call rolling on the result.

        :param min_periods: the minimum amount of observations in the window before a value is reported.
        :param center: whether to center the result, currently not supported.
        """
        # TODO We could move the partitioning to GroupBy
        from bach.partitioning import WindowFrameBoundary, WindowFrameMode, \
            Window

        if center:
            # Will never be implemented probably, as it's also deprecated in pandas
            raise NotImplementedError("centering is not implemented.")

        mode = WindowFrameMode.ROWS
        start_boundary = WindowFrameBoundary.PRECEDING
        start_value = None
        end_boundary = WindowFrameBoundary.CURRENT_ROW
        end_value = None

        index = list(self._group_by.index.values()) if self._group_by else []
        group_by = Window(group_by_columns=index,
                          order_by=self._order_by,
                          mode=mode,
                          start_boundary=start_boundary, start_value=start_value,
                          end_boundary=end_boundary, end_value=end_value,
                          min_values=min_periods)

        return DataFrame._groupby_to_frame(self, group_by)

    def sort_values(
            self,
            by: Union[str, List[str]],
            ascending: Union[bool, List[bool]] = True
    ) -> 'DataFrame':
        """
        Create a new DataFrame with the specified sorting order.

        This does not modify the current DataFrame, instead it returns a new DataFrame.

        The sorting will remain in the returned DataFrame as long as no operations are performed on that
        frame that materially change the selected data. Operations that materially change the selected data
        are for example :py:meth:`groupby`, :py:meth:`merge`, :py:meth:`materialize`, and filtering out rows.
        Adding or removing a column does not materially change the selected data.

        :param by: column label or list of labels to sort by.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `by` must also be a list and ``len(ascending) == len(by)``.
        :returns: a new DataFrame with the specified ordering.
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

    def sort_index(
        self,
        level: Optional[Level] = None,
        ascending: Union[bool, List[bool]] = True,
    ) -> 'DataFrame':
        """
        Sort dataframe by index levels.

        :param level: int or level name or list of ints or level names.
            If not specified, all index series are used
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `level` must also be a list and ``len(ascending) == len(level)``.
        :returns: a new DataFrame with the specified ordering,
         otherwise it updates the original and returns None.
        """
        sort_by = self.index_columns if level is None else self._get_indexes_by_level(level)
        df = self.sort_values(by=sort_by, ascending=ascending)
        return df

    def _get_indexes_by_level(self, level: Level) -> List[str]:
        selected_indexes = []
        nlevels = len(self.index_columns)

        for idx_l in level if isinstance(level, list) else [level]:
            if isinstance(idx_l, int) and nlevels < idx_l:
                raise ValueError(f'dataframe has only {nlevels} levels.')

            if isinstance(idx_l, str) and idx_l not in self.index_columns:
                raise ValueError(f'dataframe has no {idx_l} index level.')

            level_name = idx_l if isinstance(idx_l, str) else self.index_columns[idx_l]
            selected_indexes.append(level_name)

        return selected_indexes

    def to_pandas(self, limit: Union[int, slice] = None) -> pandas.DataFrame:
        """
        Run a SQL query representing the current state of this DataFrame against the database and return the
        resulting data as a Pandas DataFrame.

        :param limit: the limit to apply, either as a max amount of rows or a slice of the data.
        :returns: a pandas DataFrame.

        .. note::
            This function queries the database.
        """
        sql = self.view_sql(limit=limit)

        series_name_to_dtype = {}
        for series in self.all_series.values():
            pandas_info = series.to_pandas_info()
            if pandas_info is not None:
                series_name_to_dtype[series.name] = pandas_info.dtype

        with self.engine.connect() as conn:
            # read_sql_query expects a parameterized query, so we need to escape the parameter characters
            sql = escape_parameter_characters(conn, sql)
            pandas_df = pandas.read_sql_query(sql, conn, dtype=series_name_to_dtype)

        # Post-process any columns if needed. e.g. in BigQuery we represent UUIDs as text, so we convert
        # the strings that the query gives us into UUID objects
        for name, series in self.all_series.items():
            to_pandas_info = series.to_pandas_info()
            if to_pandas_info is not None and to_pandas_info.function is not None:
                pandas_df[name] = pandas_df[name].apply(to_pandas_info.function)

        if self.index:
            pandas_df = pandas_df.set_index(list(self.index.keys()))
        return pandas_df

    def head(self, n: int = 5) -> pandas.DataFrame:
        """
        Similar to :py:meth:`to_pandas` but only returns the first `n` rows.

        :param n: number of rows to query from database.
        :returns: a pandas DataFrame.

        .. note::
            This function queries the database.
        """
        return self.to_pandas(limit=n)

    def to_numpy(self) -> numpy.ndarray:
        """
        Return a Numpy representation of the DataFrame akin :py:attr:`pandas.Dataframe.to_numpy`

        :returns: Returns the values of the DataFrame as numpy.ndarray.

        .. note::
            This function queries the database.
        """
        return self.to_pandas().to_numpy()

    def _get_order_by_clause(self) -> Expression:
        """
        Get a properly formatted order by expression based on this df's order_by.
        Will return an empty Expression in case ordering is not requested.
        """
        if not self._order_by:
            return Expression.construct('')

        dialect = self.engine.dialect
        all_series_expr = {s.expression.to_sql(dialect): s.name for s in self.all_series.values()}
        if (
            self.group_by and
            not all(
                ob.expression.to_sql(dialect) in all_series_expr for ob in self._order_by
            )
        ):
            raise Exception(
                'Current order by clause is referencing expressions that are neither aggregated or grouped,'
                ' while the DataFrame itself is grouped.'
                ' Please call DataFrame.sort_values([]) or DataFrame.sort_index() for removing'
                ' sorting and try again.'
            )

        exprs = []
        fmtstr = []

        for sc in self.order_by:
            # pandas sorts by default all nulls last
            fmt = f"{{}} {'asc' if sc.asc else 'desc'} nulls last"
            if sc.expression.has_multi_level_expressions:
                multi_lvl_exprs = [
                    level_expr for level_expr in sc.expression.data if isinstance(level_expr, Expression)
                ]
                exprs.extend(multi_lvl_exprs)
                fmtstr.extend([fmt] * len(multi_lvl_exprs))
                continue

            expr = sc.expression
            if self.group_by and is_bigquery(self.engine):
                expr = Expression.column_reference(all_series_expr[expr.to_sql(dialect)])
            exprs.append(expr)
            fmtstr.append(fmt)

        return Expression.construct(f'order by {", ".join(fmtstr)}', *exprs)

    def get_current_node(
        self,
        name: str,
        limit: Union[int, slice] = None,
        distinct: bool = False,
        where_clause: Expression = None,
        having_clause: Expression = None,
        construct_multi_levels: bool = False,
    ) -> BachSqlModel:
        """
        INTERNAL: Translate the current state of this DataFrame into a SqlModel.

        :param name: The name of the new node
        :param limit: The limit to use
        :param distinct: if distinct statement needs to be applied
        :param where_clause: The where-clause to apply, if any
        :param having_clause: The having-clause to apply in case group_by is set, if any
        :param construct_multi_levels: if False, each level from a multi-level series will be treated as an
            individual column, else the column expression from the parent series will be used instead.
        :returns: SQL query as a SqlModel that represents the current state of this DataFrame.
        """
        from bach.series import SeriesAbstractMultiLevel
        self._assert_all_variables_set()

        if isinstance(limit, int):
            limit = slice(0, limit)

        limit_str: Optional[str] = None
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

        limit_clause = Expression.construct('' if limit_str is None else f'{limit_str}')
        where_clause = where_clause if where_clause else Expression.construct('')
        group_by_clause = None

        column_exprs = []
        column_names: List[str] = []

        if self.group_by:
            not_aggregated = [
                s.name for s in self._data.values()
                if not s.expression.has_aggregate_function
            ]
            if len(not_aggregated) > 0:
                raise ValueError(
                    f'The df has groupby set, but contains Series that have no aggregation '
                    f'function yet. Please make sure to first: remove these from the frame, '
                    f'setup aggregation through agg(), or on all individual series. '
                    f'Unaggregated series: {not_aggregated}'
                )

            group_by_clause = Expression.construct('')
            having_clause = having_clause if having_clause else Expression.construct('')
            group_by_column_expr = self.group_by.get_group_by_column_expression()

            if group_by_column_expr:
                group_by_clause = Expression.construct('group by {}', group_by_column_expr)

        for s in self.all_series.values():
            if not construct_multi_levels and isinstance(s, SeriesAbstractMultiLevel):
                column_names += [s.name for s in s.levels.values()]
                column_exprs += [s.get_column_expression() for s in s.levels.values()]
            else:
                column_names.append(s.name)
                column_exprs.append(s.get_column_expression())

        return CurrentNodeSqlModel.get_instance(
            dialect=self.engine.dialect,
            name=name,
            column_names=tuple(column_names),
            column_exprs=column_exprs,
            distinct=distinct,
            where_clause=where_clause,
            group_by_clause=group_by_clause,
            having_clause=having_clause,
            order_by_clause=self._get_order_by_clause(),
            limit_clause=limit_clause,
            previous_node=self.base_node,
            variables=self.variables
        )

    def view_sql(self, limit: Union[int, slice] = None) -> str:
        """
        Translate the current state of this DataFrame into a SQL query.

        This includes setting all variable values that are in self.variables.

        :param limit: the limit to apply, either as a max amount of rows or a slice of the data.
        :returns: SQL query
        """
        dialect = self.engine.dialect
        # we need to construct each multi-level series, since it should resemble the final result
        model = self.get_current_node('view_sql', limit=limit, construct_multi_levels=True)
        model = model.copy_set_materialization(Materialization.QUERY)

        placeholder_values = get_variable_values_sql(dialect=dialect, variable_values=self.variables)
        model = update_placeholders_in_graph(start_node=model, placeholder_values=placeholder_values)

        sql = to_sql(dialect=dialect, model=model)
        return sql

    def merge(
        self,
        right: DataFrameOrSeries,
        how: str = 'inner',
        on: Union[str, 'SeriesBoolean', List[Union[str, 'SeriesBoolean']]] = None,
        left_on: ColumnNames = None,
        right_on: ColumnNames = None,
        left_index: bool = False,
        right_index: bool = False,
        suffixes: Tuple[str, str] = ('_x', '_y'),
    ) -> 'DataFrame':
        """
        Join the right Dataframe or Series on self. This will return a new DataFrame that contains the
        combined columns of both dataframes, and the rows that result from joining on the specified columns.
        The columns that are joined on can consist (partially or fully) out of index columns.

        The interface of this function is similar to pandas' merge, but the following parameters are not
        supported: `sort`, `copy`, `indicator`, and `validate`.
        Additionally, when merging two frames that have conflicting columns names, and joining on indices,
        then the resulting columns/column names can differ slightly from Pandas.

        If variables are set (see :meth:`DataFrame.variables`), then values from self will be used in cases
        where a variable name/dtype combination has been defined in both the `self` and `right`
        DataFramesOrSeries.

        :param right: DataFrame or Series to join on self
        :param how: supported values: {‘left’, ‘right’, ‘outer’, ‘inner’, ‘cross’}
        :param on: optional, column(s) or condition(s) to join left and right on.
            If *on* is based on a condition (:class:`SeriesBoolean`), then self and right must have different
            base_nodes and the condition must make reference to both nodes involved in the merge.
            If multiple columns and/or conditions are specified then the clauses are joined with 'and', i.e.
            all clauses must be true to join a row in self and right.
        :param left_on: optional, column(s) from the left df to join on
        :param right_on: optional, column(s) from the right df/series to join on
        :param left_index: If true uses the index of the left df as columns to join on
        :param right_index: If true uses the index of the right df/series as columns to join on
        :param suffixes: Tuple of two strings. Will be used to suffix duplicate column names. Must make
            column names unique
        :return: A new Dataframe. The original frames are not modified.
        """
        from bach.merge import merge
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

    def _apply_func_to_series(
        self,
        func: Union[ColumnFunction, Dict[str, ColumnFunction]],
        axis: int = 1,
        numeric_only: bool = False,
        exclude_non_applied: bool = False,
        *args,
        **kwargs,
    ) -> List['Series']:
        """
        :param func: function, str, list or dict to apply to all series
            Function to use on the data. If a function, must work when passed a
            Series.

            Accepted combinations are:
            - function
            - string function name
            - list of functions and/or function names, e.g. [SeriesInt64.sum, 'mean']
            - dict of axis labels -> functions, function names or list of such.
        :param axis: the axis
        :param numeric_only: Whether to apply to numeric series only, or attempt all.
        :param exclude_non_applied: Exclude series where applying was not attempted / failed
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function

        .. note::
            Pandas has numeric_only=None to attempt all columns but ignore failing ones
            silently. This is currently not implemented.

        .. note::
            The `axis` parameter defaults to 1, because 0 is currently unsupported.
        """
        from bach.series import SeriesAbstractNumeric
        if axis == 0:
            raise NotImplementedError("Only axis=1 is currently implemented")

        if numeric_only is None:
            raise NotImplementedError("numeric_only=None to attempt all columns but ignore "
                                      "failing ones silently is currently not implemented.")

        apply_dict: Dict[str, ColumnFunction] = {}
        if isinstance(func, dict):
            # make sure the keys are series we know
            for k, v in func.items():
                if k not in self._data:
                    raise KeyError(f'{k} not found in group by series')
                if not isinstance(v, (str, list)) and not callable(v):
                    raise TypeError(f'Unsupported value type {type(v)} in func dict for key {k}')
                apply_dict[k] = v
        elif isinstance(func, (str, list)) or callable(func):
            # check whether we need to exclude non-numeric
            for name, series in self.data.items():
                if not numeric_only or isinstance(series, SeriesAbstractNumeric):
                    apply_dict[name] = func
        else:
            raise TypeError(f'Unsupported type for func: {type(func)}')

        new_series = {}
        for name, apply_func in apply_dict.items():
            for applied in self._data[name].apply_func(apply_func, *args, **kwargs):
                if applied.name in new_series:
                    raise ValueError(f'duplicate result series: {applied.name}')
                new_series[applied.name] = applied

        applied_series = list(new_series.values())
        if exclude_non_applied:
            return applied_series

        non_applied_series = [
            series.copy_override() for name, series in self._data.items() if name not in apply_dict
        ]
        return applied_series + non_applied_series

    def aggregate(self,
                  func: Union[ColumnFunction, Dict[str, ColumnFunction]],
                  axis: int = 1,
                  numeric_only: bool = False,
                  *args, **kwargs) -> 'DataFrame':
        """
        Alias for :py:meth:`agg`
        """
        return self.agg(func, axis, numeric_only, *args, **kwargs)

    def agg(
        self,
        func: Union[ColumnFunction, Dict[str, ColumnFunction]],
        axis: int = 1,
        numeric_only: bool = False,
        *args,
        **kwargs,
    ) -> 'DataFrame':
        """
        Aggregate using one or more operations over the specified axis.

        :param func: the aggregations to apply on all series. Accepted combinations are:

            * function, e.g. `SeriesInt64.sum`
            * function name
            * list of functions and/or function names, e.g. [`SeriesInt64.sum`, 'mean']
            * dict of axis labels -> functions, function names or list of such.
        :param axis: the aggregation axis. Only ``axis=1`` supported at the moment.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :param args: Positional arguments to pass through to the aggregation function
        :param kwargs: Keyword arguments to pass through to the aggregation function

        .. note::
            Pandas has ``numeric_only=None`` to attempt all columns but ignore failing ones
            silently. This is currently not implemented.

        .. note::
            The `axis` parameter defaults to 1, because 0 is currently unsupported
        """
        # todo do we want standard aggregation of index (pandas doesn't have this)?
        # todo numeric_only is a kwarg of the called func (like pandas)? ie now it breaks for nunique
        df = self
        if df.group_by is None:
            df = df.groupby()

        new_series = df._apply_func_to_series(func, axis, numeric_only,
                                              True,  # exclude_non_applied, must be positional arg.
                                              df.group_by, *args, **kwargs)

        # If the new series have a different group_by or index, we need to copy that
        if new_series:
            new_index = new_series[0].index
            new_group_by = new_series[0].group_by

        if not all(dict_name_series_equals(s.index, new_index)
                   and s.group_by == new_group_by
                   for s in new_series):
            raise ValueError("series do not agree on new index / group_by")

        return df.copy_override(
            index=new_index,
            group_by=new_group_by,
            series={s.name: s for s in new_series},
        )

    def _aggregate_func(self, func: str, axis, level, numeric_only, *args, **kwargs) -> 'DataFrame':
        """
        Return a copy of this dataframe with the aggregate function applied (but not materialized).
        :param func: sql fragment that will be applied as 'func(column_name)', e.g. 'sum'
        """

        """
        Internals documentation
        Typical execution trace, in this case for calling sum on a DataFrame:
         * df.sum()
         * df._aggregate_func('sum', ...)
         * df.agg('sum', ...)
         * df._apply_func_to_series('sum', ...)
         then per series object:
          * series.apply_func({'column': ['sum']}, ..)
          * series_subclass.sum(...)
          * series._derived_agg_func(partition, 'sum', ...)
          * series.copy_override(..., expression=Expression.construct('sum({})'))
        """
        if level is not None:
            raise NotImplementedError("index levels are currently not implemented")
        return self.agg(func, axis, numeric_only, *args, **kwargs)

    # AGGREGATES
    def count(self, axis=1, level=None, numeric_only=False, **kwargs):
        """
        Count all non-NULL values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('count', axis, level, numeric_only, **kwargs)

    # def kurt(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
    #     return self._aggregate_func('kurt', axis, level, numeric_only,
    #                                 skipna=skipna, **kwargs)
    #
    # def kurtosis(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
    #     return self._aggregate_func('kurtosis', axis, level, numeric_only,
    #                                 skipna=skipna, **kwargs)
    #
    # def mad(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
    #     return self._aggregate_func('mad', axis, level, numeric_only,
    #                                 skipna=skipna, **kwargs)

    def max(self, axis=1, skipna=True, level=None, numeric_only=False, **kwargs):
        """
        Returns the maximum of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('max', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def min(self, axis=1, skipna=True, level=None, numeric_only=False, **kwargs):
        """
        Returns the minimum of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('min', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def mean(self, axis=1, skipna=True, level=None, numeric_only=False, **kwargs):
        """
        Returns the mean of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('mean', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def median(self, axis=1, skipna=True, level=None, numeric_only=False, **kwargs):
        """
        Returns the median of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('median', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def mode(self, axis=1, skipna=True, level=None, numeric_only=False, **kwargs):
        """
        Returns the mode of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        # slight deviation from pd.mode(axis=0, numeric_only=False, dropna=True)
        return self._aggregate_func('mode', axis, level, numeric_only,
                                    skipna=skipna, **kwargs)

    def quantile(
        self,
        q: Union[float, List[float]] = 0.5,
        axis=1,
        **kwargs,
    ):
        """
        Returns the quantile per numeric/timedelta column.

        :param q: value or list of values between 0 and 1.
        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        valid_index = (
            {s.name: s for s in self._index.values() if hasattr(s, 'quantile')}
            if self.group_by is None else {}
        )
        valid_series = {
            s.name: s.copy_override(index=valid_index) for s in self._data.values() if hasattr(s, 'quantile')
        }
        if not valid_series and not valid_index:
            raise ValueError('DataFrame has no series supporting "quantile" operation.')

        df = self.copy_override(series=valid_series, index=valid_index)
        if df.group_by is None:
            df = df.groupby()

        quantiles = [q] if isinstance(q, float) else q

        all_quantile_dfs = []
        for qt in quantiles:
            new_series = df._apply_func_to_series(
                func='quantile',
                axis=axis,
                numeric_only=False,
                exclude_non_applied=True,
                partition=df.group_by,
                q=qt,
                **kwargs,
            )
            initial_series = new_series[0]
            quantile_df = df.copy_override(
                base_node=initial_series.base_node,
                series={s.name: s for s in new_series},
                index={},
                group_by=initial_series.group_by,
            )

            if quantile_df.group_by:
                # materialize the dataframe since we need to add the label for the quantile
                quantile_df = quantile_df.materialize()

            quantile_df['quantile'] = qt
            all_quantile_dfs.append(quantile_df)

        final_index = 'quantile'

        if len(quantiles) == 1:
            # if only one quantile was calculated, then we don't need to add the label on the index
            result = all_quantile_dfs[0]
            result = result[[col for col in result.data_columns if col != final_index]]
        else:
            from bach.operations.concat import DataFrameConcatOperation
            result = DataFrameConcatOperation(objects=all_quantile_dfs, ignore_index=True)()
            # q column should be in the index when calculating multiple quantiles
            result = result.set_index('quantile')

        if is_bigquery(result.engine):
            # BigQuery returns quantile per row, need to apply distinct
            result = result.materialize(node_name='bq_quantile', distinct=True)

        return result

    def nunique(self, axis=1, skipna=True, **kwargs):
        """
        Returns the number of unique values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        # deviation from horrible pd.nunique(axis=0, dropna=True)
        return self._aggregate_func('nunique', axis=axis,
                                    level=None, numeric_only=False, skipna=skipna, **kwargs)

    def round(self, decimals: int = 0):
        """
        Returns a DataFrame with rounded numerical values

        :param decimals: number of decimal places to round each numeric column
        :returns: a new DataFrame with rounded numerical columns
        """
        from bach.series import SeriesAbstractNumeric

        df = self.copy_override()
        for col in df.data.values():
            if not isinstance(col, SeriesAbstractNumeric):
                continue
            df._data[col.name] = col.round(decimals)

        return df

    # def skew(self, axis=None, skipna=True, level=None, numeric_only=False, **kwargs):
    #     return self._aggregate_func('skew', axis, level, numeric_only,
    #                                 skipna=skipna, **kwargs)
    #
    # def prod(self, axis=None, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
    #     return self._aggregate_func('prod', axis, level, numeric_only,
    #                                 skipna=skipna, min_count=min_count, **kwargs)
    #
    # def product(self, axis=None, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
    #     return self._aggregate_func('product', axis, level, numeric_only,
    #                                 skipna=skipna, min_count=min_count, **kwargs)

    def sem(self, axis=1, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        """
        Returns the unbiased standard error of the mean of each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param ddof: Delta Degrees of Freedom. Only 1 is supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('sem', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def std(self, axis=1, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        """
        Returns the sample standard deviation of each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param ddof: Delta Degrees of Freedom. Only 1 is supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('std', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def std_pop(self, axis=1, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        """
        Returns the population standard deviation of each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param ddof: Delta Degrees of Freedom. Only 1 is supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('std_pop', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def sum(self, axis=1, skipna=True, level=None, numeric_only=False, min_count=0, **kwargs):
        """
        Returns the sum of all values in each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :param min_count: This minimum amount of values (not NULL) to be present before returning a result.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('sum', axis, level, numeric_only,
                                    skipna=skipna, min_count=min_count, **kwargs)

    def var(self, axis=1, skipna=True, level=None, ddof: int = 1, numeric_only=False, **kwargs):
        """
        Returns the unbiased variance of each column.

        :param axis: only ``axis=1`` is supported. This means columns are aggregated.
        :param skipna: only ``skipna=True`` supported. This means NULL values are ignored.
        :param level: not supported.
        :param ddof: Delta Degrees of Freedom. Only 1 is supported.
        :param numeric_only: whether to aggregate numeric series only, or attempt all.
        :returns: a new DataFrame with the aggregation applied to all selected columns.
        """
        return self._aggregate_func('var', axis, level, numeric_only,
                                    skipna=skipna, ddof=ddof, **kwargs)

    def describe(
        self,
        percentiles: Optional[Sequence[float]] = None,
        include: Optional[Union[str, Sequence[str]]] = None,
        exclude: Optional[Union[str, Sequence[str]]] = None,
        datetime_is_numeric: bool = False,
    ) -> 'DataFrame':
        """
        Returns descriptive statistics.
        The following statistics are considered: `count`, `mean`, `std`, `min`, `max`, `nunique` and `mode`

        :param percentiles: list of percentiles to be calculated. Values must be between 0 and 1.
        :param include: dtypes to be included.
            Either a sequence of dtypes, a single dtype, or the special value 'all'.
            By default calculations will be based on numerical columns, if there are any
            numerical columns and on all columns if there are no numerical columns.
        :param exclude: dtypes to be excluded. Either a sequence of dtypes, a single dtype, or None.
        :param datetime_is_numeric: not supported
        :returns: a new DataFrame with the descriptive statistics
        """
        from bach.operations.describe import DataFrameDescribeOperation
        return DataFrameDescribeOperation(
            obj=self,
            include=include,
            exclude=exclude,
            datetime_is_numeric=datetime_is_numeric,
            percentiles=percentiles,
        )()

    def create_variable(
        self,
        name: str,
        value: Any,
        *,
        dtype: Optional[str] = None,
    ) -> Tuple['DataFrame', 'Series']:
        """
        Create a Series object that can be used as a variable, within the returned DataFrame. The
        DataFrame will have the variable with the given values set in :meth:`DataFrame.variables`.

        The variable value can later be changed using :meth:`DataFrame.set_variable`

        **Multiple variables with the same name**

        For variables the combination (name, dtype) uniquely identifies a variable. That means that there
        can be multiple variables with the same name, if they are of different types. This is counter to
        how a lot of programming languages handle variables. But it prevents a lot of error conditions and
        edge cases around merging DataFrames and Series with the same variables, and building on top of
        SqlModels that already have variables.

        :param name: name of variable to update
        :param value: value of variable
        :param dtype: optional. If not set it will be derived from the value, if set we check that it
            matches the value. If dtype doesn't match the value's dtype, then an Exception is raised.
        :return: Tuple with DataFrame and the Series object that can be used as a variable.
        """
        from bach.series.series import variable_series
        series = variable_series(base=self, value=value, name=name)
        if dtype is not None and dtype != series.dtype:
            raise ValueError(f"Dtype of value ({series.dtype}) and provided dtype ({dtype}) don't match.")
        variables = self.variables
        variables[DtypeNamePair(dtype=series.dtype, name=name)] = value
        df = self.copy_override(variables=variables)
        return df, series

    def set_variable(self, name: str, value: Any, *, dtype: Optional[str] = None) -> 'DataFrame':
        """
        Return a copy of this DataFrame with the variable value updated.

        :param name: name of variable to update
        :param value: new value of variable
        :param dtype: optional. If not set it will be derived from the value, if set we check that it
            matches the value. If dtype doesn't match the value's dtype, then an Exception is raised.
        :return: copy of this DataFrame, with the value updated.
        """
        df, _ = self.create_variable(name, value, dtype=dtype)
        return df

    def get_all_variable_usage(self) -> List[DefinedVariable]:
        """
        Get all variables that influence the values of this DataFrame.
        This includes both variables that are used in the current `self.series`, but also variables that
        were used in earlier steps, i.e. in the SqlModels of `self.base_node`.

        The output of this method can be useful for diagnosing issues with variables. If a variable is used
        multiple times, then it will appear here multiple times. If a variable has conflicting definitions
        then the conflicting dtypes and/or values are all returned.

        **Returned data**

        This method returns a list of DefinedVariable tuples, the fields in the tuples:

        * name: name of the variable
        * dtype: dtype
        * value: value that is currently set in `self.variables`, or None if there is no value
        * ref_path: If the variable is used in an already materialized part of the DataFrame, i.e.
          the usage is in self.base_node, then this is the reference path from self.base_node to the
          SqlModel in which the variable usage occurs. If the variable is used in self.series instead,
          then this is None
        * old_value: If the variable is used in an already materialized part of the DataFrame, then it
          also has a value already. That is this value. Will be None if this variable usage is not in
          self.base_node.

        :return: List with all usages of variables in this DataFrame.
        """
        return self._get_all_used_variables_series() + self._get_all_used_variables_base_node()

    def _get_all_used_variables_series(self) -> List[DefinedVariable]:
        all_tokens = []
        for series in self.all_series.values():
            all_tokens.extend(series.expression.get_all_tokens())
        variable_tokens = [token for token in all_tokens if isinstance(token, VariableToken)]

        result = []
        for vt in variable_tokens:
            dtype_name = DtypeNamePair(dtype=vt.dtype, name=vt.name)
            value = None if dtype_name not in self.variables else self.variables[dtype_name]
            result.append(
                DefinedVariable(name=vt.name, dtype=vt.dtype, value=value, ref_path=None, old_value=None)
            )
        return result

    def _get_all_used_variables_base_node(self) -> List[DefinedVariable]:
        result = []
        all_placeholders = get_all_placeholders(self.base_node)
        for placeholder_name, values_dict in all_placeholders.items():
            token = VariableToken.placeholder_name_to_token(placeholder_name)
            if token is None:
                continue
            for ref_path, old_value in values_dict.items():
                dtype_name = token.dtype_name
                value = None if dtype_name not in self.variables else self.variables[dtype_name]
                result.append(
                    DefinedVariable(
                        name=dtype_name.name, dtype=dtype_name.dtype,
                        value=value, ref_path=ref_path, old_value=old_value)
                )
        return result

    def _assert_all_variables_set(self):
        """
        Asserts that all variables used in the series are set. Raises an Exception if a variable is not set.
        """
        used_variables = self._get_all_used_variables_series()
        for var in used_variables:
            dtype_name = DtypeNamePair(dtype=var.dtype, name=var.name)
            if dtype_name not in self.variables:
                raise Exception(f'Variable {dtype_name.name}, with dtype {dtype_name.dtype} is used, '
                                f'but not set. Use create_variable() to assign a value')

    def append(
        self,
        other: Union['DataFrame', List['DataFrame']],
        ignore_index: bool = False,
        sort: bool = False,
    ) -> 'DataFrame':
        """
        Append rows of other dataframes to the the caller dataframe.
        Non-shared columns between dataframes are added to the caller.

        :param other: objects to be added
        :param ignore_index: if true, drops indexes of all object to be appended
        :param sort: if true, columns are sorted alphanumerically

        :return: a new dataframe with all rows from appended Dataframes.
        """
        from bach.operations.concat import DataFrameConcatOperation
        if isinstance(other, list) and not other:
            raise ValueError('no dataframe or series to append.')

        other_dfs = other if isinstance(other, list) else [other]
        concatenated_df = DataFrameConcatOperation(
            objects=[self] + other_dfs,
            ignore_index=ignore_index,
            sort=sort,
        )()
        return concatenated_df

    def drop_duplicates(
        self,
        subset: Optional[Union[str, Sequence[str]]] = None,
        keep: Union[str, bool] = 'first',
        ignore_index: bool = False,
        sort_by: Optional[Union[str, Sequence[str]]] = None,
        ascending: Union[bool, List[bool]] = True,
    ) -> 'DataFrame':
        """
        Return a dataframe with duplicated rows removed based on all series labels or a subset of labels.

        :param subset: series label or sequence of labels.
            Duplications to be dropped are based on the combination of the subset of series.
            If not provided, all series labels will be used by default.
        :param keep: Supported values: "first", "last" and False. Determines which duplicates to keep:

            * `first`: drop all occurrences except the first one
            * `last`:  drop all occurrences except the last one
            * False: drops all duplicates

            If no value is provided, first occurrences will be kept by default.
        :param ignore_index: if true, drops indexes of the result
        :param sort_by: series label or sequence of labels used to sort values.
            Sorting of values is needed since result might be non-deterministic
            when keep == "first" or keep == "last". If not provided:
            1. If dataframe has already an order_by, first and last values will be performed based on it
            2. Else all series not considered in duplication will be used instead.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `by` must also be a list and ``len(ascending) == len(by)``.

        :return: a new dataframe with dropped duplicates.
        """
        if keep not in ('first', 'last', False):
            raise ValueError('keep must be either "first", "last" or False.')

        subset = self._get_parsed_subset_of_data_columns(subset)
        sort_by = self._get_parsed_subset_of_data_columns(sort_by)

        df = self.copy() if not ignore_index else self.reset_index(drop=True)

        dedup_on = list(subset or self.data_columns)
        dedup_data = [name for name in df.all_series if name not in dedup_on]

        # in case df has no order_by and no sort_by was provided
        # it will use the series that are not included in dedup_on
        dedup_sort = list(sort_by or dedup_data) if sort_by or not self.order_by else []

        # dedup_data contains index series if ignore_index = False
        # in this case we should append those as data_columns
        if dedup_data and not ignore_index:
            df = df.reset_index(drop=False)

        # drop all duplicates
        if keep is False:
            freq_df = df[dedup_on]
            freq_df['freq'] = 1
            freq_df = freq_df.groupby(by=dedup_on).sum()
            freq_df = freq_df.reset_index(drop=False)

            df = df.merge(freq_df, on=dedup_on)
            df = df[df.freq_sum == 1][dedup_on + dedup_data]
        elif dedup_data:
            from bach.partitioning import WindowFrameBoundary
            if keep == 'last':
                func_to_apply = 'window_last_value'
                # unbounded following is required only when last value is needed
                end_boundary = WindowFrameBoundary.FOLLOWING
            else:
                func_to_apply = 'window_first_value'
                end_boundary = WindowFrameBoundary.CURRENT_ROW

            if dedup_sort:
                df = df.sort_values(by=dedup_sort, ascending=ascending)

            df = df.groupby(by=dedup_on).window(end_boundary=end_boundary, end_value=None)
            df = df[dedup_data].agg(func=func_to_apply).reset_index(drop=False)
            df = df.rename(columns={f'{ddd}_{func_to_apply}': ddd for ddd in dedup_data})
            # consider sorting only in window
            df._order_by = []

        # we need to just apply distinct for 'first' and 'last'.
        if keep:
            node_name = f'drop_duplicates_' + '_'.join(dedup_on)
            df = df.materialize(distinct=True, node_name=node_name)
            # respect initial order by
            df._order_by = self._order_by

        df = df if ignore_index else df.set_index(keys=self.index_columns)
        return df

    def value_counts(
        self,
        subset: Optional[List[str]] = None,
        normalize: bool = False,
        sort: bool = True,
        ascending: bool = False,
    ) -> 'Series':
        """
        Returns a series containing counts of each unique row in the DataFrame

        :param subset: a list of series labels to be used when counting. If subset is not provided and
            dataframe has no group_by, all data columns will be used. In case the DataFrame has a group_by,
            series in group_by will be added to subset.
        :param normalize: returns proportions instead of frequencies
        :param sort: sorts result by frequencies
        :param ascending: sorts values in ascending order if true.

        :return: a series containing all counts per unique row.
        """
        if not subset:
            subset = self.data_columns
        elif any(s not in self.data_columns for s in subset):
            raise ValueError('subset contains invalid series.')

        if self.group_by:
            # consider groupby series in subset
            subset = list(self.group_by.index.keys()) + subset

        df = self.copy_override(
            series={
                s: self.all_series[s].copy_override(index={}, group_by=None) for s in subset
            },
            index={},
            group_by=None,
        )
        df['value_counts'] = 1
        df = df.groupby(by=list(subset)).sum()

        if normalize:
            df = df.materialize()
            df._data['value_counts_sum'] /= df['value_counts_sum'].sum()  # type: ignore

        df = df.rename(columns={'value_counts_sum': 'value_counts'})

        if sort:
            return df._data['value_counts'].sort_values(ascending=ascending)

        return df._data['value_counts']

    def dropna(
        self,
        *,
        axis: int = 0,
        how: str = 'any',
        thresh: Optional[int] = None,
        subset: Optional[Union[str, Sequence[str]]] = None,
    ) -> 'DataFrame':
        """
        Removes rows with missing values (NaN, None and SQL NULL).

        :param axis: only ``axis=0`` is supported. This means rows that contain missing values are dropped.
        :param how: determines when a row is removed. Supported values:

            - 'any': rows with at least one missing value are removed
            - 'all': rows with all missing values are removed

        :param thresh: determines the least amount of non-missing values a row needs to have
            in order to be kept
        :param subset: series label or sequence of labels to be considered for missing values.
            If subset is None, all DataFrame's series labels will be used.
            In case subset is an empty list, a copy from the DataFrame will
            be returned.

        :return: a new dataframe with dropped rows.
        """
        if axis:
            raise ValueError('only axis = 0 is supported.')

        if how not in ('any', 'all'):
            raise ValueError(f'{how} is not a valid value for "how" parameter.')

        subset = self._get_parsed_subset_of_data_columns(subset)
        dropna_series = self.data_columns if subset is None else subset

        if not dropna_series:
            return self.copy()

        logical_operator = 'or' if how == 'any' else 'and'

        conditions = []
        for ds in dropna_series:
            main_condition = self.all_series[ds].isnull()
            if self.all_series[ds].dtype in ['float64', 'int64']:
                main_condition = main_condition | (self.all_series[ds] == float('nan'))

            conditions.append(main_condition)

        if not thresh:
            expression_fmt = f' {logical_operator} '.join([f'{{}}'] * len(dropna_series))
        else:
            # we need to add the amount of nullables in the row and compare it to the thresh
            cases_fmt = f' + '.join([f'case when {{}} then 1 else 0 end'] * len(dropna_series))
            expression_fmt = f'{len(self.data_columns)} - ({cases_fmt}) < {thresh}'

        drop_row_series = conditions[0].copy_override(
            expression=Expression.construct(expression_fmt, *conditions),
        )

        dropna_df = self[~drop_row_series]
        assert isinstance(dropna_df, DataFrame)

        return dropna_df

    def fillna(
        self,
        *,
        value: Union[
            Union['Series', AllSupportedLiteralTypes],
            Dict[str, Union[AllSupportedLiteralTypes, 'Series']]
        ] = None,
        method: Optional[str] = None,
        axis: int = 0,
        sort_by: Optional[Union[str, Sequence[str]]] = None,
        ascending: Union[bool, List[bool]] = True,
    ) -> 'DataFrame':
        """
        Fill any NULL value using a method or with a given value.

        :param value: A literal/series to fill all NULL values on each series
            or a dictionary specifying which literal/series to use for each series.
        :param method: Method to use for filling NULL values on all DataFrame series. Supported values:

            - "ffill"/"pad": Fill missing values by propagating the last non-nullable value in the series.
            - "bfill"/"backfill": Fill missing values with the next non-nullable value in the series.

        :param axis: only ``axis=0`` is supported.
        :param sort_by: series label or sequence of labels used to sort values.
            Sorting of values is needed since result might be non-deterministic, as rows with NULLs might
            yield different results affecting the values to be propagated when using a filling method.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `sort_by` must also be a list and ``len(ascending) == len(sort_by)``.

        :return: a new dataframe with filled missing values.

        .. note::
            sort_by is required if method is specified and the DataFrame has no order_by.

        .. warning::
            If sort_by is non-deterministic, this operation might yield different results after
            performing other operations over the resultant dataframe.
        """
        df = self.copy()
        if method and value is not None:
            raise ValueError('cannot specify both "method" and "value".')

        if method:
            from bach.operations.value_propagation import ValuePropagation
            df = ValuePropagation(df=df, method=method).propagate(sort_by, ascending)

        if value is not None:
            series_to_fill = list(value.keys()) if isinstance(value, dict) else self.data_columns
            for s in series_to_fill:
                fill_with = value[s] if isinstance(value, dict) else value
                df[s] = df.all_series[s].fillna(fill_with)

        return df

    def ffill(
        self,
        sort_by: Optional[Union[str, Sequence[str]]] = None,
        ascending: Union[bool, List[bool]] = True,
    ) -> 'DataFrame':
        """
        Fill missing values by propagating the last non-nullable value in each series.

        :param sort_by: series label or sequence of labels used to sort values.
            Sorting of values is needed since result might be non-deterministic, as rows with NULLs might
            yield different results affecting the values to be propagated when using a filling method.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `sort_by` must also be a list and ``len(ascending) == len(sort_by)``.

        :return: a new dataframe with filled missing values.

        .. note::
            sort_by is required if DataFrame has no order_by.

        .. warning::
            If sort_by is non-deterministic, this operation might yield different results after
            performing other operations over the resultant dataframe.
        """
        from bach.operations.value_propagation import ValuePropagation
        v_propagation = ValuePropagation(df=self, method='ffill')
        return v_propagation.propagate(sort_by=sort_by, ascending=ascending)

    def bfill(
        self,
        sort_by: Optional[Union[str, Sequence[str]]] = None,
        ascending: Union[bool, List[bool]] = True,
    ) -> 'DataFrame':
        """
        Fill missing values by using the next non-nullable value in each series.

        :param sort_by: series label or sequence of labels used to sort values.
            Sorting of values is needed since result might be non-deterministic, as rows with NULLs might
            yield different results affecting the values to be propagated when using a filling method.
        :param ascending: Whether to sort ascending (True) or descending (False). If this is a list, then the
            `sort_by` must also be a list and ``len(ascending) == len(sort_by)``.

        :return: a new dataframe with filled missing values.

        .. note::
            sort_by is required if DataFrame has no order_by.

        .. warning::
            If sort_by is non-deterministic, this operation might yield different results after
            performing other operations over the resultant dataframe.
        """
        from bach.operations.value_propagation import ValuePropagation
        v_propagation = ValuePropagation(df=self, method='bfill')
        return v_propagation.propagate(sort_by=sort_by, ascending=ascending)

    def _get_parsed_subset_of_data_columns(
        self, subset: Optional[Union[str, Sequence[str]]],
    ) -> Optional[Sequence[str]]:
        subset = [subset] if isinstance(subset, str) else subset
        if subset and any(s not in self.data_columns for s in subset):
            raise ValueError(
                f'subset param contains invalid series: {sorted(set(subset) - set(self.data_columns))}'
            )
        return subset

    def stack(self, dropna: bool = True) -> 'Series':
        """
        Stacks all data_columns into a single index series.

        :param dropna: Whether to drop rows that contain missing values. If the caller has
            at least an index series, this might generate different combinations between
            the index and the stacked values.

        :return: a reshaped series that includes a new index (named "__stacked_index")
            containing the caller's column labels as values.

        .. note::
            ``level`` parameter is not supported since multilevel columns are not allowed.
        """
        df = self.copy()
        if df.group_by:
            df = df.materialize('stack')

        dc_dfs = []
        # convert each data column series to DataFrame and use series name as new index value
        for series_name, series in df.data.items():
            dc_df = series.copy_override(name='__stacked').to_frame()
            dc_df['__stacked_index'] = series_name
            dc_dfs.append(dc_df)

        # concat all dataframes to get new_index and stacked values in two single series
        from bach.operations.concat import DataFrameConcatOperation
        stacked_df = DataFrameConcatOperation(dc_dfs)()

        # append the stacked index to the initial indexes
        stacked_df = stacked_df.set_index(list(self.index_columns + ['__stacked_index']))
        stacked_df = stacked_df.dropna() if dropna else stacked_df

        return stacked_df.all_series['__stacked']

    def scale(self, with_mean: bool = True, with_std: bool = True) -> 'DataFrame':
        """
        Standardizes all numeric series based on mean and population standard deviation.

        :param with_mean: if true, each feature value will be centered before scaling
        :param with_std: if true, each feature value will be scaled to unit variance

        :return: DataFrame

        Each transformation per feature is performed as follows:

        .. testsetup:: scale
           :skipif: engine is None

           import pandas
           data = {'index': ['a', 'b', 'c', 'd'], 'feature': [1, 2, 3, 4]}
           pdf = pandas.DataFrame(data)
           df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
           df = df.set_index('index')
           agg_df = df.agg(['mean', 'std_pop'], numeric_only=True)

           feature = df['feature']
           mean_feature = agg_df['feature_mean']
           std_feature = agg_df['feature_std_pop']
           with_mean = True
           with_std = True

        .. doctest:: scale
            :skipif: engine is None

            >>> scaled_feature = feature.copy()
            >>> if with_mean:
            ...     scaled_feature -= mean_feature


            >>> if with_std:
            ...     scaled_feature /= std_feature

        Where:
            * ``feature`` is the series to be scaled
            * ``mean_feature`` is the mean of ``feature``
            * ``std_feature`` is the (population-based) stardard deviation of ``feature``

        """
        from bach.preprocessing.scalers import StandardScaler
        return StandardScaler(training_df=self, with_mean=with_mean, with_std=with_std).transform()

    def minmax_scale(self, feature_range: Tuple[int, int] = (0, 1)) -> 'DataFrame':
        """
        Scales all numeric series based on a given range.

        :param feature_range: ``tuple(min, max)`` desired range to use for scaling.
        :return: DataFrame

        Each transformation per feature is performed as follows:

        .. testsetup:: minmax_scale
           :skipif: engine is None

           import pandas
           data = {'index': ['a', 'b', 'c', 'd'], 'feature': [1, 2, 3, 4]}
           pdf = pandas.DataFrame(data)

           df = DataFrame.from_pandas(engine=engine, df=pdf, convert_objects=True)
           df = df.set_index('index')
           agg_df = df.agg(['min', 'max'], numeric_only=True)
           agg_df = agg_df.merge(df, how='cross')

           feature = df['feature']
           min_feature = agg_df['feature_min']
           max_feature = agg_df['feature_max']

        .. doctest:: minmax_scale
            :skipif: engine is None

            >>> range_min,  = (0, 1)
            >>> feature_std = (feature - min_feature) / (max_feature - min_feature)
            >>> scaled_feature = feature_std * (range_max - range_min) + range_min

        Where:
            * ``feature`` is the series to be scaled
            * ``feature_min`` is the minimum value of ``feature``
            * ``feature_max`` is the maximum value of ``feature``
            * ``range_min, range_max`` = ``feature_range``
        """
        from bach.preprocessing.scalers import MinMaxScaler
        return MinMaxScaler(training_df=self, feature_range=feature_range).transform()

    def unstack(
        self,
        level: Union[str, int] = -1,
        fill_value: Optional[AllSupportedLiteralTypes] = None,
        aggregation: str = 'max'
    ) -> 'DataFrame':
        """
        Pivot a level of the index labels.

        Returns a(n unsorted) DataFrame with the values of the unstacked index as columns. In case of
        duplicate index values that are unstacked, `aggregation` is used to aggregate the values.

        DataFrame's index should be of at least two levels to unstack.

        :param level: selects the level of the index that is unstacked.
        :param fill_value: replace missing values resulting from unstacking. Should be of same type as the
            series that is unstacked.
        :param aggregation: method of aggregation, in case of duplicate index values. Supports all aggregation
            methods that :py:meth:`aggregate` supports.

        :return: DataFrame

        .. note::
            This function queries the database.
        """
        if len(self.index) <= 1:
            raise NotImplementedError('index must be a multi level index to unstack')

        if isinstance(level, int) and level >= len(self.index):
            raise IndexError(f'Too many levels. DataFrame/Series has only {len(self.index)} levels.')

        if isinstance(level, str) and level not in self.index:
            raise IndexError(f'"{level}" does not exist in DataFrame/Series index')

        if type(aggregation) != str:
            raise TypeError('invalid aggregation method')

        level_index = level if isinstance(level, int) else self.index_columns.index(level)
        index_to_unstack = self.index_columns[level_index]

        from bach.series import SeriesAbstractMultiLevel
        if isinstance(self.index[index_to_unstack], SeriesAbstractMultiLevel):
            raise IndexError(f'"{level}" cannot be unstacked, since it is a MultiLevel series.')

        values = self.index[index_to_unstack].unique(skipna=False).to_numpy()

        if None in values or numpy.nan in values:
            raise ValueError("index contains empty values, cannot be unstacked")

        remaining_indexes = [idx_col for idx_col in self.index_columns if idx_col != index_to_unstack]
        df = self.reset_index(level=index_to_unstack, drop=False)

        new_columns = []
        for column in values:
            for curr_col in self.data_columns:
                new_column_name = f'{column}__{curr_col}'
                new_columns.append(new_column_name)

                df[new_column_name] = None
                # previous statement will change dtype to string because value is None
                df[new_column_name] = df[new_column_name].astype(df[curr_col].dtype)
                df.loc[df[index_to_unstack] == column, new_column_name] = df[curr_col]

        df = df.groupby(remaining_indexes).aggregate(aggregation)
        df = df.rename(columns={col: col.replace(f'_{aggregation}', '') for col in df.data_columns})

        # materialization is needed since df might be sorted by columns that no longer exist
        df._order_by = []
        df = df.materialize('unstack')
        df = df[new_columns]

        return df.fillna(value=fill_value)

    def get_dummies(
        self,
        prefix: Optional[Union[str, List[str], Dict[str, str]]] = None,
        prefix_sep: str = '_',
        dummy_na: bool = False,
        columns: Optional[List[str]] = None,
        dtype: str = 'int64',
    ) -> 'DataFrame':
        """
        Convert each unique category/value from a string series into a dummy/indicator variable.

        :param prefix: String to append to each new column name. By default, the prefix will be the name of
            the series the category is originated from.
        :param prefix_sep: Separated between the prefix and label.
        :param dummy_na: If true, it will include ``nan`` as a variable.
        :param columns: List of string series to be converted.
        :param dtype: dtype of all new columns
        :return: DataFrame

        .. note::
            DataFrame should contain at least one index level.
        """
        if not self.index:
            raise IndexError('DataFrame/Series should have at least one index level.')

        if columns:
            columns_to_encode = columns
        else:
            columns_to_encode = [s.name for s in self.data.values() if s.dtype == 'string']

        if not columns_to_encode:
            return self.copy()

        invalid_columns = [
            col for col in columns_to_encode
            if col not in self.data or self.data[col].dtype != 'string'
        ]
        if invalid_columns:
            raise ValueError(f'{invalid_columns} are not valid columns.')

        prefix_per_col = {}
        if isinstance(prefix, dict):
            prefix_per_col = prefix
        elif prefix is not None:
            prefix_per_col = {
                col: prefix
                for col, prefix in zip(columns_to_encode, (prefix if isinstance(prefix, list) else [prefix]))
            }

        categorical_series = []
        from bach.series.series import value_to_series
        df_cp = self.copy()

        # prepare each series, add prefix to each value (variable identifiers)
        for col in columns_to_encode:
            if dummy_na:
                df_cp.loc[df_cp[col].isnull(), col] = 'nan'

            text_series = df_cp[col]
            prefix_val = f'{prefix_per_col.get(col, col)}{prefix_sep}'
            prefix_series = value_to_series(text_series, value=prefix_val, name=col)
            text_series = prefix_series + text_series

            categorical_series.append(text_series)

        from bach.operations.concat import SeriesConcatOperation
        # concat all categorical series into a single series, this way we avoid unstacking per each series
        categorical_df = SeriesConcatOperation(categorical_series)().to_frame()
        categorical_df = categorical_df.dropna()
        categorical_df['values'] = 1
        categorical_df = categorical_df.set_index(categorical_df.data_columns[0], append=True)
        dummies_df = categorical_df['values'].unstack()

        remaining_columns = [dc for dc in self.data_columns if dc not in columns_to_encode]
        dummy_columns = dummies_df.data_columns

        # merge the encoded variables with the rest of series, replace null values
        encoded_df = self[remaining_columns].merge(dummies_df, how='left', left_index=True, right_index=True)
        encoded_df = encoded_df.fillna(value=dict(zip(dummy_columns, [0] * len(dummy_columns))))
        encoded_df[dummy_columns] = encoded_df[dummy_columns].astype(dtype)
        return encoded_df


def dict_name_series_equals(a: Dict[str, 'Series'], b: Dict[str, 'Series']):
    """
    Compare two dicts in the format that we use to track series and indices.
    A normal == does not work on these dicts, because Series.equals() is overridden to create SeriesBoolean,
    so we need to call Series.equals instead.
    """
    return (a is None and b is None) or (
            len(a) == len(b) and list(a.keys()) == list(b.keys())
            and all(ai.equals(bi) for (ai, bi) in zip(a.values(), b.values()))
    )
