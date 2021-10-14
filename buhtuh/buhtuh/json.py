"""
Copyright 2021 Objectiv B.V.
"""
from typing import Union


class Json:
    def __init__(self, series_object):
        self._series_object = series_object

    # todo use expression instead of self._series_object.name
    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            expression = f'{self._series_object.expression}->{key}'
        elif isinstance(key, slice):
            if key.step:
                raise NotImplementedError('slice steps not supported')
            if key.stop is not None:
                negative_stop = ''
                if key.stop < 0:
                    negative_stop = f'json_array_length({self._series_object.name})'
                stop = f'{negative_stop} {key.stop} - 1'
            if key.start is not None:
                negative_start = ''
                if key.start < 0:
                    negative_start = f'json_array_length({self._series_object.name})'
                start = f'{negative_start} {key.start}'
                if key.stop is not None:
                    where = f'between {start} and {stop}'
                else:
                    where = f'>= {start}'
            else:
                where = f'<= {stop}'
            expression = f"""(select json_agg(x.value)
            from json_array_elements({self._series_object.name}) with ordinality x
            where ordinality - 1 {where})"""
        else:
            TypeError(f'key should be int or slice, actual type: {type(key)}')

        return self._series_object._get_derived_series('json', expression)

    def get_value(self, key: str, as_str=False):
        '''
        as_str: if True, it returns a string, else json
        '''
        return_as_string_operator = ''
        return_dtype = 'json'
        if as_str:
            return_as_string_operator = '>'
            type = 'string'
        expression = f"{self._series_object.expression}->{return_as_string_operator}'{key}'"
        return self._series_object._get_derived_series(return_dtype, expression)

    # objectiv features below:
    @property
    def cookie_id(self):
        expression = f"""(select (array_agg(value->>'cookie_id'))[1]
        from json_array_elements({self._series_object.name})
        where value ->> '_type' = 'CookieIdContext')"""
        return self._series_object._get_derived_series('string', expression)

    @property
    def user_agent(self):
        expression = f"""(select (array_agg(value->>'user_agent'))[1]
        from json_array_elements({self._series_object.name})
        where value ->> '_type' = 'HttpContext')"""
        return self._series_object._get_derived_series('string', expression)

    @property
    def nice_name(self):
        expression = f"""(
        select array_to_string(
            array_agg(
                replace(
                    regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                ' Context', '') || ': ' || (value ->> 'id')
            ),
        ' => ')
        from json_array_elements({self._series_object.name}) with ordinality
        where ordinality = json_array_length({self._series_object.name})) || case
            when json_array_length({self._series_object.name}) > 1
                then ' located at ' || (select array_to_string(
            array_agg(
                replace(
                    regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                ' Context', '') || ': ' || (value ->> 'id')
            ),
        ' => ')
        from json_array_elements({self._series_object.name}) with ordinality
        where ordinality = json_array_length({self._series_object.name})
        ) else '' end"""
        return self._series_object._get_derived_series('string', expression)
