"""
Copyright 2021 Objectiv B.V.
"""
import json
from typing import Dict, Union, TYPE_CHECKING, Tuple, cast, Optional, List, Any

from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression
from bach.series.series import WrappedPartition, ToPandasInfo
from bach.sql_model import BachSqlModel
from bach.types import DtypeOrAlias, StructuredDtype, AllSupportedLiteralTypes, Dtype
from sql_models.constants import DBDialect
from sql_models.util import quote_string, is_postgres, DatabaseNotSupportedException, is_bigquery

if TYPE_CHECKING:
    from bach.series import SeriesBoolean, SeriesString
    from bach.partitioning import GroupBy


class SeriesJson(Series):
    """
    A Series that represents the JSON type and its specific operations.

    Depending on the database this Series is backed by different database types:

    * On Postgres this utilizes the native 'jsonb' database type.
    * On BigQuery this utilizes the generic 'STRING' database type.

    .. note::
        On Postgres, SeriesJson does not use the 'json' database type, but the 'jsonb' type, As the 'json'
        type has limited functionality.

        This class is the standard and recommended type to use for handling json like data. Having said that,
        there is a special SeriesJsonPostgres type that uses the 'json' data type on Postgres, but internally
        that casts all data to 'jsonb' too.

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
    """

    # TODO: support instance_dtype to return better types
    dtype = 'json'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'jsonb',
        # on BigQuery we use STRING for JSONs. Of course SeriesString is the default class for that, so
        # here we set None
        DBDialect.BIGQUERY: None
    }
    supported_value_types = (dict, list)

    return_dtype = 'json'

    @property
    def json(self):
        """
        .. _json_accessor:

        Get access to json operations via the class that's return through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: JsonPostgresAccessor
            :members:
            :special-members: __getitem__

        """
        if is_postgres(self.engine):
            return JsonPostgresAccessor(series_object=self)
        if is_bigquery(self.engine):
            return JsonBigQueryAccessor(series_object=self)
        raise DatabaseNotSupportedException(self.engine)

    @property
    def elements(self):
        return self.json

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        if is_postgres(dialect):
            return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', literal)
        if is_bigquery(dialect):
            return literal
        raise DatabaseNotSupportedException(dialect)

    @classmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: Union[dict, list],
            dtype: StructuredDtype
    ) -> Expression:
        cls.assert_engine_dialect_supported(dialect)
        json_value = json.dumps(value)
        return Expression.string_value(json_value)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if is_postgres(dialect):
            if source_dtype in ('json', 'json_postgres'):
                # SeriesJsonPostgres is a special case: SeriesJsonPostgres.expression already contains a cast
                # to the database type 'jsonb', so we actually don't need to do any conversion
                return expression
            if source_dtype == 'string':
                return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)
            raise ValueError(f'cannot convert {source_dtype} to json')
        if is_bigquery(dialect):
            if source_dtype in ('json', 'string'):
                return expression
            raise ValueError(f'cannot convert {source_dtype} to json')
        raise DatabaseNotSupportedException(dialect)

    def to_pandas_info(self) -> Optional['ToPandasInfo']:
        if is_bigquery(self.engine):
            # All data is stored as string, so if we actually want the objects, we need to load the string
            # as json.
            return ToPandasInfo('object', self._json_loads)
        return None

    @staticmethod
    def _json_loads(data: Optional[str]) -> Optional[Any]:
        """ Helper of to_pandas_info """
        if data is None:
            return None
        try:
            return json.loads(data)
        except ValueError as exc:
            raise ValueError(f'invalid json content in result: {data}') from exc

    def _comparator_operation(
        self,
        other: Union['Series', AllSupportedLiteralTypes],
        comparator: str,
        other_dtypes=tuple()
    ) -> 'SeriesBoolean':
        if is_postgres(self.engine):
            other_dtypes = ('json_postgres', 'json', 'string')
            fmt_str = f'cast({{}} as jsonb) {comparator} cast({{}} as jsonb)'
        elif is_bigquery(self.engine):
            other_dtypes = ('json', 'string')
            fmt_str = f'{{}} {comparator} {{}}'
        else:
            raise DatabaseNotSupportedException(self.engine)

        result = self._binary_operation(
            other, operation=f"comparator '{comparator}'",
            fmt_str=fmt_str,
            other_dtypes=other_dtypes, dtype='bool'
        )
        return cast('SeriesBoolean', result)  # we told _binary_operation to return dtype='bool'

    def __le__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        if is_postgres(self.engine):
            return self._comparator_operation(other, "<@")
        message_override = f'Operator <= is not supported for type json on database {self.engine.name}'
        raise DatabaseNotSupportedException(self.engine, message_override=message_override)

    def __ge__(self, other: Union['Series', AllSupportedLiteralTypes]) -> 'SeriesBoolean':
        if is_postgres(self.engine):
            return self._comparator_operation(other, "@>")
        message_override = f'Operator >= is not supported for type json on database {self.engine.name}'
        raise DatabaseNotSupportedException(self.engine, message_override=message_override)

    def min(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()

    def max(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()


class SeriesJsonPostgres(SeriesJson):
    """
    A special Series that represents the 'json' database type on Postgres.

    .. note::
        Generally, it is advised to use :class:`JsonSeries` instead. Given a `SeriesJsonPostgres` object,
        calling `json_series_pg.astype('json')` will return a `JsonSeries` class representing the same data.

    When `json` data is encountered in a sql table, this dtype is used. On Postgres for all operations the
    data is first cast to jsonb type. Therefore, it is recommended to cast to :class:`JsonSeries` directly.

    The public interface of this class is the same as the :py:class:`SeriesJson` class. See the docstring
    of that class for more information.
    """

    dtype = 'json_postgres'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'json',
    }
    return_dtype = 'json'

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

    def materialize(
            self,
            node_name='manual_materialize',
            limit: Any = None,
            distinct: bool = False,
    ):
        """
        Instance of this Series cannot be materialized, as the base expression is not just the column name
        but a cast to 'jsonb'.

        Use class:`SeriesJson` instead, which can be materialized.
        """
        raise Exception(f'{self.__class__.__name__} cannot be materialized.')


class JsonBigQueryAccessor:
    """
    class with accessor methods to JSON type data columns on BigQuery.
    """
    def __init__(self, series_object: 'SeriesJson'):
        self._series_object = series_object

    def __getitem__(self, key: Union[str, int, slice]):
        """
        Slice the JSON data in pythonic ways
        """
        # TODO: leverage instance_dtype information here, if we have that
        if isinstance(key, int):
            if key >= 0:
                expression = Expression.construct(f'''JSON_QUERY({{}}, '$[{key}]')''', self._series_object)
                return self._series_object.copy_override(expression=expression)
            # case key <= 0
            # BigQuery doesn't (yet) natively support this, so we emulate this.
            expr_len = Expression.construct('ARRAY_LENGTH(JSON_EXTRACT_ARRAY({}))', self._series_object)
            expr_offset = Expression.construct(f'OFFSET({{}} {key})', expr_len)
            expression = Expression.construct('JSON_EXTRACT_ARRAY({})[{}]', self._series_object, expr_offset)
            return self._series_object.copy_override(expression=expression)

        elif isinstance(key, str):
            return self.get_value(key)

        elif isinstance(key, slice):
            if key.step:
                raise NotImplementedError('slice steps not supported')
            raise NotImplementedError()  # TODO

        raise TypeError('Key should either be a string, integer, or slice.')

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'SeriesJson']:
        """
        Select values from objects by key. This works only on scalar values! to get json objects use
        __getitem__, that is, object['key']

        :param key: the key to return the values for.
        :param as_str: if True, it returns a string Series, json otherwise.
        :returns: series with the selected object value.
        """
        # TODO: ESCAPE KEY!
        # note: escaping is function dependent. for JSON_VALUE[1]: 'If a JSON key uses invalid JSONPath
        # characters, then you can escape those characters using double quotes.'
        # [1] https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#json_value
        assert '"' not in key

        expression = Expression.construct(f'''JSON_QUERY({{}}, '$."{key}"')''', self._series_object)

        if not as_str:
            return self._series_object.copy_override(expression=expression)
        from bach.series import SeriesString
        return self._series_object.copy_override(expression=expression).copy_override_type(SeriesString)


class JsonPostgresAccessor:
    """
    class with accessor methods to SeriesJson data on Postgres.
    """
    def __init__(self, series_object: 'SeriesJson'):
        self._series_object = series_object
        self._return_dtype: Dtype = series_object.return_dtype

    def __getitem__(self, key: Union[str, int, slice]):
        """
        Slice the JSON data in pythonic ways
        """
        if isinstance(key, int):
            return self._series_object\
                .copy_override_dtype(dtype=self._return_dtype)\
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
                .copy_override_dtype(dtype=self._return_dtype)\
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
        """
        Select values from objects by key. Same as using `.json[key]` on the json column.

        :param key: the key to return the values for.
        :param as_str: if True, it returns a string Series, jsonb otherwise.
        :returns: series with the selected object value.
        """
        return_as_string_operator = ''
        return_dtype = self._return_dtype
        if as_str:
            return_as_string_operator = '>'
            return_dtype = 'string'
        expression = Expression.construct(f"{{}}->{return_as_string_operator}{{}}",
                                          self._series_object,
                                          Expression.string_value(key))
        return self._series_object\
            .copy_override_dtype(dtype=return_dtype)\
            .copy_override(expression=expression)
