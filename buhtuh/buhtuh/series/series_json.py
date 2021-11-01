"""
Copyright 2021 Objectiv B.V.
"""
import json
from typing import Optional, Dict, Union, TYPE_CHECKING, Any

from buhtuh.series import BuhTuhSeries, const_to_series
from buhtuh.expression import Expression, quote_string, quote_identifier
from sql_models.model import SqlModel

if TYPE_CHECKING:
    from buhtuh.series import BuhTuhSeriesBoolean
    from buhtuh.partitioning import BuhTuhGroupBy


class BuhTuhSeriesJsonb(BuhTuhSeries):
    """
    this a proper class, not just a string subclass
    """
    dtype = 'jsonb'
    # todo can only assign a type to one series type, and object is quite generic
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'jsonb'
    supported_value_types = (dict, list)

    def __init__(self,
                 engine,
                 base_node: SqlModel,
                 index: Dict[str, 'BuhTuhSeries'],
                 name: str,
                 expression: Expression,
                 group_by: 'BuhTuhGroupBy',
                 sorted_ascending: Optional[bool] = None):
        super().__init__(engine=engine,
                         base_node=base_node,
                         index=index,
                         name=name,
                         expression=expression,
                         group_by=group_by,
                         sorted_ascending=sorted_ascending)
        self.json = Json(self)

    def __getitem__(self, key: Union[Any, slice]):
        # this method is overridden because there is not pandas dtype for json(b)
        if isinstance(key, slice):
            raise NotImplementedError("index slices currently not supported")

        # any other value we treat as a literal index lookup
        # multiindex not supported atm
        if not self.index:
            raise Exception('Function not supported on Series without index')
        if len(self.index) != 1:
            raise NotImplementedError('Index only implemented for simple indexes.')
        series = self.to_frame()[list(self.index.values())[0] == key]
        assert isinstance(series, self.__class__)

        # this is massively ugly
        return series.head(1).values[0]

    @classmethod
    def supported_value_to_expression(cls, value: Union[dict, list]) -> Expression:
        json_value = json.dumps(value)
        return Expression.construct('cast({} as jsonb)', Expression.string_value(json_value))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype in ['jsonb', 'json']:
            return expression
        if source_dtype != 'string':
            raise ValueError(f'cannot convert {source_dtype} to jsonb')
        return Expression.construct('cast({} as jsonb)', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['json', 'jsonb'], other)
        expression = Expression.construct(
            f'cast({{}} as jsonb) {comparator} cast({{}} as jsonb)',
            self.expression, other.expression
        )
        return self.copy_override(dtype='bool', expression=expression)

    def __le__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "<@")

    def __ge__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._comparator_operator(other, "@>")


class BuhTuhSeriesJson(BuhTuhSeriesJsonb):
    """
    this a proper class, not just a string subclass
    """
    dtype = 'json'
    dtype_aliases = tuple()  # type: ignore
    supported_db_dtype = 'json'

    def __init__(self,
                 engine,
                 base_node: SqlModel,
                 index: Dict[str, 'BuhTuhSeries'],
                 name: str,
                 expression: Expression,
                 group_by: 'BuhTuhGroupBy',
                 sorted_ascending: Optional[bool] = None):

        super().__init__(engine=engine,
                         base_node=base_node,
                         index=index,
                         name=name,
                         expression=Expression.construct(f'cast({{}} as jsonb)', expression),
                         group_by=group_by,
                         sorted_ascending=sorted_ascending)


class Json:
    def __init__(self, series_object):
        self._series_object = series_object

    def __getitem__(self, key: Union[str, int, slice]):
        if isinstance(key, int):
            return self._series_object.copy_override(
                dtype='jsonb',
                expression=Expression.construct(f'{{}}->{key}', self._series_object)
            )
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
            return self._series_object.copy_override(
                dtype='jsonb',
                expression=Expression.construct(
                    combined_expression,
                    *([self._series_object] * expression_references)
                ))
        raise TypeError(f'key should be int or slice, actual type: {type(key)}')

    def _find_in_json_list(self, key: Union[str, Dict[str, str]]):
        if isinstance(key, (dict, str)):
            key = json.dumps(key)
            quoted_key = quote_string(key)
            expression_str = f"""(select min(case when ({quoted_key}::jsonb) <@ value
            then ordinality end) -1 from jsonb_array_elements({{}}) with ordinality)"""
            return expression_str
        else:
            raise TypeError(f'key should be int or slice, actual type: {type(key)}')

    def get_value(self, key: str, as_str=False):
        '''
        as_str: if True, it returns a string, else json
        '''
        return_as_string_operator = ''
        return_dtype = 'jsonb'
        if as_str:
            return_as_string_operator = '>'
            return_dtype = 'string'
        expression = Expression.construct(f"{{}}->{return_as_string_operator}{{}}",
                                          self._series_object,
                                          Expression.string_value(key))
        return self._series_object.copy_override(dtype=return_dtype, expression=expression)

    # objectiv features below:
    def get_from_context_with_type_series(self, type, key, dtype='string'):
        expression_str = f'''
        jsonb_path_query_first({{}},
        \'$[*] ? (@._type == $type)\',
        \'{{"type":{quote_identifier(type)}}}\') ->> {{}}'''
        expression = Expression.construct(
            expression_str,
            self._series_object,
            Expression.string_value(key)
        )
        return self._series_object.copy_override(dtype=dtype, expression=expression)

    @property
    def feature_stack(self):
        keys = ['_type', 'id']
        jsonb_build_object_str = [f"{quote_string(key)}, value -> {quote_string(key)}" for key in keys]
        expression_str = f'''(select jsonb_agg(jsonb_build_object({", ".join(jsonb_build_object_str)}))
        from jsonb_array_elements({{}}))'''
        expression = Expression.construct(
            expression_str,
            self._series_object
        )
        return self._series_object.copy_override(dtype='jsonb', expression=expression)

    @property
    def navigation_features(self):
        return self[{'_type': 'NavigationContext'}: None]

    @property
    def cookie_id(self):
        return self.get_from_context_with_type_series("CookieIdContext", "cookie_id")

    @property
    def user_agent(self):
        return self.get_from_context_with_type_series("HttpContext", "user_agent")

    @property
    def application(self):
        return self.get_from_context_with_type_series("ApplicationContext", "id")

    @property
    def nice_name(self):
        expression = Expression.construct(
            f"""(
            select array_to_string(
                array_agg(
                    replace(
                        regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                    ' Context', '') || ': ' || (value ->> 'id')
                ),
            ' => ')
            from jsonb_array_elements({{}}) with ordinality
            where ordinality = jsonb_array_length({{}})) || case
                when jsonb_array_length({{}}) > 1
                    then ' located at ' || (select array_to_string(
                array_agg(
                    replace(
                        regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                    ' Context', '') || ': ' || (value ->> 'id')
                ),
            ' => ')
            from jsonb_array_elements({{}}) with ordinality
            where ordinality < jsonb_array_length({{}})
            ) else '' end""",
            self._series_object,
            self._series_object,
            self._series_object,
            self._series_object,
            self._series_object
        )
        return self._series_object.copy_override(dtype='string', expression=expression)
