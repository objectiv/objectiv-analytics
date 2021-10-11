"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC

from buhtuh import const_to_series, BuhTuhSeries


class BuhTuhSeriesBoolean(BuhTuhSeries, ABC):
    dtype = 'bool'
    dtype_aliases = ('boolean', '?', bool)
    supported_db_dtype = 'boolean'
    supported_value_types = (bool, )

    @classmethod
    def value_to_sql(cls, value: bool) -> str:
        if not isinstance(value, cls.supported_value_types):
            raise TypeError(f'value should be bool, actual type: {type(value)}')
        return str(value)

    @staticmethod
    def from_dtype_to_sql(source_dtype: str, expression: str) -> str:
        if source_dtype == 'bool':
            return expression
        else:
            if source_dtype not in ['int64', 'string']:
                raise ValueError(f'cannot convert {source_dtype} to bool')
            return f'({expression})::bool'

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['bool'], other)
        expression = f'({self.expression}) {comparator} ({other.expression})'
        return self._get_derived_series('bool', expression)

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
