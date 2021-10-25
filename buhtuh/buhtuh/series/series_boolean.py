"""
Copyright 2021 Objectiv B.V.
"""
from abc import ABC

from buhtuh.series import BuhTuhSeries, const_to_series
from buhtuh.expression import Expression


class BuhTuhSeriesBoolean(BuhTuhSeries, ABC):
    dtype = 'bool'
    dtype_aliases = ('boolean', '?', bool)
    supported_db_dtype = 'boolean'
    supported_value_types = (bool, )

    @classmethod
    def supported_value_to_expression(cls, value: bool) -> Expression:
        # 'True' and 'False' are valid boolean literals in Postgres
        # See https://www.postgresql.org/docs/14/datatype-boolean.html
        return Expression.raw(str(value))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'bool':
            return expression
        if source_dtype not in ['int64', 'string']:
            raise ValueError(f'cannot convert {source_dtype} to bool')
        return Expression.construct('cast({} as bool)', expression)

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['bool'], other)
        expression = Expression.construct(f'({{}}) {comparator} ({{}})', self, other)
        return self._get_derived_series('bool', expression)

    def _boolean_operator(self, other, operator: str) -> 'BuhTuhSeriesBoolean':
        # TODO maybe "other" should have a way to tell us it can be a bool?
        # TODO we're missing "NOT" here. https://www.postgresql.org/docs/13/functions-logical.html
        other = const_to_series(base=self, value=other)
        self._check_supported(f"boolean operator '{operator}'", ['bool', 'int64', 'float'], other)
        if other.dtype != 'bool':
            expression = Expression.construct(f'(({{}}) {operator} cast({{}} as bool))', self, other)
        else:
            expression = Expression.construct(f'(({{}}) {operator} ({{}}))', self, other)
        return self._get_derived_series('bool', expression)

    def __and__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._boolean_operator(other, 'AND')

    def __or__(self, other) -> 'BuhTuhSeriesBoolean':
        return self._boolean_operator(other, 'OR')
