"""
Copyright 2021 Objectiv B.V.
"""
import json
from typing import Optional, Any, Dict, Union, TYPE_CHECKING, List, Tuple

from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression
from bach.series.series import WrappedPartition
from bach.sql_model import BachSqlModel
from bach.types import DtypeOrAlias, StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import quote_string, is_postgres, DatabaseNotSupportedException

if TYPE_CHECKING:
    from bach.series import SeriesBoolean
    from bach.partitioning import GroupBy


class SeriesJsonb(Series):
    """
    A Series that represents the postgres jsonb type and its specific operations.

    This is the standard and recommended type to use for handling json like data.

    **Getting data**

    It is possible to get a selection of data from the json in the json type column. For selecting data from
    json, arrays and objects are supported. The data can be selected using `.json[]` on the json column

    Selecting data from an array is based on position. It works similar to slicing through python lists.

    .. note::

        Slicing is only possible if *all* values in the column are lists or None.

    Selecting from objects is possible by key.

    Examples:

     .. testsetup:: jsonb
        :skipif: engine is None

        data = ['["a","b","c"]', '["d","e","f","g"]', '[{"h":"i","j":"k"},{"l":["m","n","o"]},{"p":"q"}]']
        pdf = pd.DataFrame(data=data, columns=['jsonb_column'])
        df = DataFrame.from_pandas(engine, pdf, convert_objects=True)
        df['jsonb_column'] = df.jsonb_column.astype('jsonb')

    .. doctest:: jsonb
        :skipif: engine is None

        >>> pdf
                                                jsonb_column
        0                                      ["a","b","c"]
        1                                  ["d","e","f","g"]
        2  [{"h":"i","j":"k"},{"l":["m","n","o"]},{"p":"q"}]

    .. doctest:: jsonb
        :skipif: engine is None

        >>> df = DataFrame.from_pandas(engine, pdf, convert_objects=True)
        >>> df['jsonb_column'] = df.jsonb_column.astype('jsonb')
        >>> # load some json strings and convert them to jsonb type
        >>> # slice and show with .head()
        >>> df.jsonb_column.json[:2].head()
        _index_0
        0                                            [a, b]
        1                                            [d, e]
        2    [{'h': 'i', 'j': 'k'}, {'l': ['m', 'n', 'o']}]
        Name: jsonb_column, dtype: object

    .. doctest:: jsonb
        :skipif: engine is None

        >>> df.jsonb_column.json[1].head()
        _index_0
        0                         b
        1                         e
        2    {'l': ['m', 'n', 'o']}
        Name: jsonb_column, dtype: object

    .. doctest:: jsonb
        :skipif: engine is None

        >>> # selecting from objects is done by entering a key:
        >>> df.jsonb_column.json[1].json['l'].head()
        _index_0
        0         None
        1         None
        2    [m, n, o]
        Name: jsonb_column, dtype: object

    A last case is selecting based on the objects *in* an array.
    With this method, a dict is passed in the `.json[]` selector. The value of the first match with the dict
    to the objects in a json array is returned for the `.json[]` selector. A match is when all key/value pairs
    of the dict are found in an object. This can be used for selecting a subset of a json array with objects.

    .. doctest:: jsonb
        :skipif: engine is None

        >>> # selecting from arrays by searching objects in the array.
        >>> df.jsonb_column.json[:{"j":"k"}].head()
        _index_0
        0                      None
        1                      None
        2    [{'h': 'i', 'j': 'k'}]
        Name: jsonb_column, dtype: object

    .. doctest:: jsonb
        :skipif: engine is None

        >>> # or:
        >>> df.jsonb_column.json[{"l":["m","n","o"]}:].head()
        _index_0
        0                                    None
        1                                    None
        2    [{'l': ['m', 'n', 'o']}, {'p': 'q'}]
        Name: jsonb_column, dtype: object

    **Database support and types**

    * Postgres: utilizes the 'jsonb' database type.
    * BigQuery: json support coming soon
    """
    dtype = 'jsonb'
    # todo can only assign a type to one series type, and object is quite generic
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'jsonb',
    }
    supported_value_types = (dict, list)
    return_dtype = dtype

    class Json:
        """
        class with accessor methods to json(b) type data columns.
        """
        def __init__(self, series_object: 'SeriesJsonb'):
            self._series_object = series_object

        def __getitem__(self, key: Union[str, int, slice]):
            """
            Slice this jsonb database object in pythonic ways:

            :param key: A very mixed key to slice on, please see below.

            .. testsetup:: jsonb__getitem__
                :skipif: engine is None

                data = [
                    '["a","b","c"]', '["d","e","f","g"]', '[{"h":"i","j":"k"},{"l":["m","n","o"]},{"p":"q"}]',
                ]
                pdf = pd.DataFrame(data=data, columns=['jsonb_column'])
                df = DataFrame.from_pandas(engine, pdf, convert_objects=True)
                df['jsonb_column'] = df.jsonb_column.astype('jsonb')

            .. doctest:: jsonb__getitem__
                :skipif: engine is None

                >>> # slice and show with .head()
                >>> df.jsonb_column.json[:2].head()
                _index_0
                0                                            [a, b]
                1                                            [d, e]
                2    [{'h': 'i', 'j': 'k'}, {'l': ['m', 'n', 'o']}]
                Name: jsonb_column, dtype: object

            .. doctest:: jsonb__getitem__
                :skipif: engine is None

                >>> # selecting one position returns the single entry:
                >>> df.jsonb_column.json[1].head()
                _index_0
                0                         b
                1                         e
                2    {'l': ['m', 'n', 'o']}
                Name: jsonb_column, dtype: object

            .. doctest:: jsonb__getitem__
                :skipif: engine is None

                >>> # selecting from objects is done by entering a key:
                >>> df.jsonb_column.json[1].json['l'].head()
                _index_0
                0         None
                1         None
                2    [m, n, o]
                Name: jsonb_column, dtype: object

            Or select based on the objects *in* an array.
            With this method, a dict is passed in the `.json[]` selector. The value of the first match with
            the dict to the objects in a json array is returned for the `.json[]` selector. A match is when
            all key/value pairs of the dict are found in an object. This can be used for selecting a subset
            of a json array with objects.

            .. doctest:: jsonb__getitem__
                :skipif: engine is None

                >>> # selecting from arrays by searching objects in the array.
                >>> df.jsonb_column.json[:{"j":"k"}].head()
                _index_0
                0                      None
                1                      None
                2    [{'h': 'i', 'j': 'k'}]
                Name: jsonb_column, dtype: object

            .. doctest:: jsonb__getitem__
                :skipif: engine is None

                >>> # or:
                >>> df.jsonb_column.json[{"l":["m","n","o"]}:].head()
                _index_0
                0                                    None
                1                                    None
                2    [{'l': ['m', 'n', 'o']}, {'p': 'q'}]
                Name: jsonb_column, dtype: object
            """
            if isinstance(key, int):
                return self._series_object\
                    .copy_override_dtype(dtype=self._series_object.return_dtype)\
                    .copy_override(expression=Expression.construct(f'{{}}->{key}', self._series_object))
            elif isinstance(key, str):
                return self.get_value(key)
            elif isinstance(key, slice):
                expression_references = 0
                if key.step:
                    raise NotImplementedError('slice steps not supported')
                if key.stop is not None:
                    negative_stop = ''
                    if isinstance(key.stop, int):
                        if key.stop < 0:
                            negative_stop = f'jsonb_array_length({{}})'
                            expression_references += 1
                        stop = f'{negative_stop} {key.stop} - 1'
                    elif isinstance(key.stop, (dict, str)):
                        stop = self._find_in_json_list(key.stop)
                        expression_references += 1
                    else:
                        raise TypeError('cant')
                if key.start is not None:
                    if isinstance(key.start, int):
                        negative_start = ''
                        if key.start < 0:
                            negative_start = f'jsonb_array_length({{}})'
                            expression_references += 1
                        start = f'{negative_start} {key.start}'
                    elif isinstance(key.start, (dict, str)):
                        start = self._find_in_json_list(key.start)
                        expression_references += 1
                    else:
                        raise TypeError('cant')
                    if key.stop is not None:
                        where = f'between {start} and {stop}'
                    else:
                        where = f'>= {start}'
                else:
                    where = f'<= {stop}'
                combined_expression = f"""(select jsonb_agg(x.value)
                from jsonb_array_elements({{}}) with ordinality x
                where ordinality - 1 {where})"""
                expression_references += 1
                return self._series_object\
                    .copy_override_dtype(dtype=self._series_object.return_dtype)\
                    .copy_override(
                        expression=Expression.construct(
                            combined_expression,
                            *([self._series_object] * expression_references)
                        )
                    )
            raise TypeError(f'key should be int or slice, actual type: {type(key)}')

        def _find_in_json_list(self, key: Union[str, Dict[str, str]]):
            if isinstance(key, (dict, str)):
                key = json.dumps(key)
                quoted_key = quote_string(self._series_object.engine, key)
                expression_str = f"""(select min(case when ({quoted_key}::jsonb) <@ value
                then ordinality end) -1 from jsonb_array_elements({{}}) with ordinality)"""
                return expression_str
            else:
                raise TypeError(f'key should be int or slice, actual type: {type(key)}')

        def get_value(self, key: str, as_str: bool = False):
            '''
            Select values from objects by key. Same as using `.json[key]` on the json column.

            :param key: the key to return the values for.
            :param as_str: if True, it returns a string Series, jsonb otherwise.
            :returns: series with the selected object value.
            '''
            return_as_string_operator = ''
            return_dtype = self._series_object.return_dtype
            if as_str:
                return_as_string_operator = '>'
                return_dtype = 'string'
            expression = Expression.construct(f"{{}}->{return_as_string_operator}{{}}",
                                              self._series_object,
                                              Expression.string_value(key))
            return self._series_object\
                .copy_override_dtype(dtype=return_dtype)\
                .copy_override(expression=expression)

    @property
    def json(self):
        """
        .. _json_accessor:

        Get access to json operations via the class that's return through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: bach.SeriesJsonb.Json
            :members:
            :special-members: __getitem__

        """
        return self.Json(self)

    @property
    def elements(self):
        return self.Json(self)

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if not is_postgres(dialect):
            raise DatabaseNotSupportedException(dialect)
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)

    @classmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: Union[dict, list],
            dtype: StructuredDtype
    ) -> Expression:
        json_value = json.dumps(value)
        return Expression.string_value(json_value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype in ['jsonb', 'json']:
            return expression
        if source_dtype != 'string':
            raise ValueError(f'cannot convert {source_dtype} to jsonb')
        return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)

    def _comparator_operation(self, other, comparator, other_dtypes=('json', 'jsonb')):
        return self._binary_operation(
            other, operation=f"comparator '{comparator}'",
            fmt_str=f'cast({{}} as jsonb) {comparator} cast({{}} as jsonb)',
            other_dtypes=other_dtypes, dtype='bool'
        )

    def __le__(self, other) -> 'SeriesBoolean':
        return self._comparator_operation(other, "<@")

    def __ge__(self, other) -> 'SeriesBoolean':
        return self._comparator_operation(other, "@>")

    def min(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()

    def max(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()

    def materialize(
            self,
            node_name='manual_materialize',
            limit: Any = None,
            distinct: bool = False,
    ):
        raise Exception(f'{self.__class__.__name__} cannot be materialized.')


class SeriesJson(SeriesJsonb):
    """
    A Series that represents the json type.

    When `json` data is encountered in a sql table, this dtype is used. In the underlying sql, the data is
    cast to the jsonb type. As a result all methods of the :py:class:`SeriesJsonb` can also be used with this
    `json` type series.

    **Database support and types**

    * Postgres: utilizes the 'json' database type.
    * BigQuery: support coming soon
    """
    dtype = 'json'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'json',
    }
    return_dtype = 'jsonb'

    def __init__(self,
                 engine,
                 base_node: BachSqlModel,
                 index: Dict[str, 'Series'],
                 name: str,
                 expression: Expression,
                 group_by: 'GroupBy',
                 sorted_ascending: Optional[bool],
                 index_sorting: List[bool],
                 instance_dtype: StructuredDtype,
                 **kwargs):

        super().__init__(engine=engine,
                         base_node=base_node,
                         index=index,
                         name=name,
                         expression=Expression.construct(f'cast({{}} as jsonb)', expression),
                         group_by=group_by,
                         sorted_ascending=sorted_ascending,
                         index_sorting=index_sorting,
                         instance_dtype=instance_dtype,
                         **kwargs)
