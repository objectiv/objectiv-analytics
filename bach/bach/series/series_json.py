"""
Copyright 2021 Objectiv B.V.
"""
import json
from abc import abstractmethod
from typing import Dict, Union, TYPE_CHECKING, Tuple, cast, Optional, List, Any, TypeVar, Generic

from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression
from bach.series.series import WrappedPartition, ToPandasInfo
from bach.sql_model import BachSqlModel
from bach.types import DtypeOrAlias, StructuredDtype, AllSupportedLiteralTypes, Dtype
from sql_models.constants import DBDialect
from sql_models.util import quote_string, is_postgres, DatabaseNotSupportedException, is_bigquery

if TYPE_CHECKING:
    from bach.series import SeriesBoolean, SeriesString, SeriesInt64
    from bach.partitioning import GroupBy


class SeriesJson(Series):
    """
    A Series that represents the JSON type and its specific operations.


    **Database support and types**

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

    @property
    def json(self) -> 'JsonAccessor':
        """
        Get access to json operations via the class that's returned through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: bach.series.series_json.JsonAccessor
            :members:

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

    @property
    def json(self) -> 'JsonAccessor':
        """
        Get access to json operations via the class that's returned through this accessor.
        Use as `my_series.json.get_value()` or `my_series.json[:2]`

        .. autoclass:: bach.series.series_json.JsonAccessor
            :members:
        """
        json_series = self.astype('json')
        assert isinstance(json_series, SeriesJson)  # help mypy
        return JsonPostgresAccessor(series_object=json_series)

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


TSeriesJson = TypeVar('TSeriesJson', bound='SeriesJson')


class JsonAccessor(Generic[TSeriesJson]):
    """
    Abstract class with accessor methods to JSON type data.

    Database specific subclasses implement the abstract functions.
    """
    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object

    def __getitem__(self, key: Union[str, int, slice]) -> 'TSeriesJson':
        """
        Slice the JSON data in pythonic ways
        """
        # TODO: leverage instance_dtype information here, if we have that
        if isinstance(key, int):
            return self._get_array_item(key)

        elif isinstance(key, str):
            return self._get_dict_item(key)

        elif isinstance(key, slice):
            return self._get_array_slice(key)

        raise TypeError('Key should either be a string, integer, or slice.')

    @abstractmethod
    def _get_array_slice(self, key: slice) -> 'TSeriesJson':
        """
        Get items from toplevel array.

        This assumes the top-level item in the json is an array. Will result in an exception (later on) if
        that's not the case!

        :param key: array-slice.
        :returns: series with the selected values.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_array_item(self, key: int) -> 'TSeriesJson':
        """
        Get item from toplevel array.

        This assumes the top-level item in the json is an array. Will result in an exception (later on) if
        that's not the case!

        :param key: the 0-based index. If negative this will count from the end of the array (1 based). The
            index MUST exist in the array
        :returns: series with the selected value.
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_dict_item(self, key: str) -> 'TSeriesJson':
        """
        Get item from toplevel object by key.

        This assumes the top-level item in the json is an object. Will result in an exception (later on) if
        that's not the case!

        :param key: the key to return the values for.
        :returns: series with the selected value.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """
        Get item from toplevel object by key.

        :param key: the key to return the values for.
        :param as_str: if True, it returns a string Series, json otherwise.
        :returns: series with the selected object value.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_array_length(self) -> 'SeriesInt64':
        """
        Get the length of the toplevel array.

        This assumes the top-level item in the json is an array. Will result in an exception (later on) if
        that's not the case!
        """
        # Implementing a more generic __len__() function is not trivial as a json object can be (among
        # others) an array, a dict, or a string, all of which should be supported by a generic __len__().
        # So for now we have a dedicated len function for arrays.
        raise NotImplementedError()


class JsonBigQueryAccessor(JsonAccessor, Generic[TSeriesJson]):
    """
    BigQuery specific implementation of JsonAccessor.
    """

    def _get_array_slice(self, key: slice) -> 'TSeriesJson':
        """ See implementation in parent class :class:`JsonAccessor` """
        if key.step:
            raise NotImplementedError('slice steps not supported')

        start_expression = self._get_slice_partial_expr(value=key.start, is_start=True)
        stop_expression = self._get_slice_partial_expr(value=key.stop, is_start=False)

        values_expression = Expression.construct(
            "select val "
            "from unnest(JSON_QUERY_ARRAY({}, '$')) val with offset as pos "
            "where pos >= {} and pos < {} "
            "order by pos",
            self._series_object, start_expression, stop_expression
        )
        json_str_expression = Expression.construct(
            "'[' || ARRAY_TO_STRING(ARRAY({}), ', ') || ']'",
            values_expression
        )
        return self._series_object\
            .copy_override(expression=json_str_expression)

    def _get_slice_partial_expr(self, value: Optional[int], is_start: bool) -> Expression:
        """
        Return expression for either the lower bound or upper bound of a slice.

        Assumes that self._series_object is an array!

        :param value: slice.start or slice.stop
        :param is_start: whether value is the slice.start (True) or slice.stop (False) value
        :return: Expression that will evaluate to an integer that can be used to compare against positions
                    in the array.
        """
        if value is not None and not isinstance(value, int):
            raise TypeError(f'Slice value must be None or an integer, value: {value}')

        if value is None:
            if is_start:
                # return index of first item in the array
                return Expression.construct('0')
            else:
                # return index that is guaranteed to be beyond the last item in the array
                max_int = 2 ** 63 - 1
                return Expression.construct(f'{max_int}')
        elif value >= 0:
            return Expression.construct(f'{value}')
        else:
            array_len = self.get_array_length()
            return Expression.construct(f'({{}} {value})', array_len)

    def _get_array_item(self, key: int) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        if key >= 0:
            expression = Expression.construct(f'''JSON_QUERY({{}}, '$[{key}]')''', self._series_object)
            return self._series_object.copy_override(expression=expression)
        # case key < 0
        # BigQuery doesn't (yet) natively support this, so we emulate this.
        array_len = self.get_array_length()
        expr_offset = Expression.construct(f'OFFSET({{}} {key})', array_len)
        expression = Expression.construct('JSON_QUERY_ARRAY({})[{}]', self._series_object, expr_offset)
        return self._series_object.copy_override(expression=expression)

    def _get_dict_item(self, key: str) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return cast('TSeriesJson', self.get_value(key=key, as_str=False))

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        # TODO: as_str is never used?
        # Special characters are tricky. According to the latests jsonpath spec draft we should use the
        # index selector [1] (e.g. `$['key with special characters']`). But BigQuery only supports the dot
        # selector [2][3]. However BigQuery does allow us to quote the key when using the dot selector [4],
        # which is not in the jsonpath draft spec. So we quote the key, and just raise an exception if
        # anybody tries to use a key that contains a quote.
        # [1] https://www.ietf.org/archive/id/draft-ietf-jsonpath-base-05.html#name-index-selector
        # [2] https://www.ietf.org/archive/id/draft-ietf-jsonpath-base-05.html#name-dot-selector
        # [3] https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#JSONPath_format
        # [4] https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
        if '"' in key:
            raise ValueError(f'key values containing double quotes are not supported. key: {key}')

        json_expression = Expression.construct(
            '''JSON_QUERY({}, '$."{}"')''',
            self._series_object,
            Expression.raw(key)
        )

        if not as_str:
            return self._series_object.copy_override(expression=json_expression)
        from bach.series import SeriesString
        value_expression = Expression.construct(
            '''JSON_VALUE({}, '$."{}"')''',
            self._series_object,
            Expression.raw(key)
        )
        expression = Expression.construct('COALESCE({}, {})', value_expression, json_expression)
        return self._series_object.copy_override(expression=expression).copy_override_type(SeriesString)

    def get_array_length(self) -> 'SeriesInt64':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        # Implementing a more generic __len__() function is not trivial as a json object can be (among
        # others) an array, a dict, or a string, all of which should be supported by a generic __len__().
        # So for now we have a dedicated len function for arrays.
        from bach.series import SeriesInt64
        expression = Expression.construct('ARRAY_LENGTH(JSON_QUERY_ARRAY({}))', self._series_object)
        return self._series_object \
            .copy_override_type(SeriesInt64) \
            .copy_override(expression=expression)


class JsonPostgresAccessor(JsonAccessor, Generic[TSeriesJson]):
    """
    Postgres specific implementation of JsonAccessor.
    """

    def _find_in_json_list(self, key: Union[str, Dict[str, str]]):
        if isinstance(key, (dict, str)):
            key = json.dumps(key)
            quoted_key = quote_string(self._series_object.engine, key)
            expression_str = f"""(select min(case when ({quoted_key}::jsonb) <@ value
            then ordinality end) -1 from jsonb_array_elements({{}}) with ordinality)"""
            return expression_str
        else:
            raise TypeError(f'key should be int or slice, actual type: {type(key)}')

    def _get_array_slice(self, key: slice) -> 'TSeriesJson':
        """ See implementation in parent class :class:`JsonAccessor` """
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
            if key.stop is not None:
                where = f'<= {stop}'
            else:
                # no start and no stop: we want to select all elements.
                where = 'is not null'  # should be true for all ordinalities.
        combined_expression = f"""(select jsonb_agg(x.value)
        from jsonb_array_elements({{}}) with ordinality x
        where ordinality - 1 {where})"""
        expression_references += 1
        non_null_expression = f"coalesce({combined_expression}, '[]'::jsonb)"
        return self._series_object \
            .copy_override(
                expression=Expression.construct(
                    non_null_expression,
                    *([self._series_object] * expression_references)
                )
            )

    def _get_array_item(self, key: int) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return self._series_object \
            .copy_override(expression=Expression.construct(f'{{}}->{key}', self._series_object))

    def _get_dict_item(self, key: str) -> 'TSeriesJson':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        return cast('TSeriesJson', self.get_value(key=key, as_str=False))

    def get_value(self, key: str, as_str: bool = False) -> Union['SeriesString', 'TSeriesJson']:
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """

        if '"' in key:
            raise ValueError(f'key values containing double quotes are not supported. key: {key}')

        return_as_string_operator = ''
        if as_str:
            return_as_string_operator = '>'
        expression = Expression.construct(f"{{}}->{return_as_string_operator}{{}}",
                                          self._series_object,
                                          Expression.string_value(key))
        result = self._series_object.copy_override(expression=expression)
        if as_str:
            from bach.series import SeriesString
            return result.copy_override_type(SeriesString)
        return result

    def get_array_length(self) -> 'SeriesInt64':
        """ For documentation, see implementation in parent class :class:`JsonAccessor` """
        from bach.series import SeriesInt64
        expression = Expression.construct('jsonb_array_length({})', self._series_object)
        return self._series_object \
            .copy_override_type(SeriesInt64) \
            .copy_override(expression=expression)
