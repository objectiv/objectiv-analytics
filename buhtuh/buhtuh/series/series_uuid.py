"""
Copyright 2021 Objectiv B.V.
"""
from typing import Union
from uuid import UUID

from buhtuh import DataFrameOrSeries
from buhtuh.series import BuhTuhSeries, const_to_series
from buhtuh.expression import Expression


class BuhTuhSeriesUuid(BuhTuhSeries):
    """
    Series representing UUID values.
    """
    dtype = 'uuid'
    dtype_aliases = ()
    supported_db_dtype = 'uuid'
    supported_value_types = (UUID, str)

    @classmethod
    def supported_value_to_expression(cls, value: Union[UUID, str]) -> Expression:
        if isinstance(value, str):
            # Check that the string value is a valid UUID by converting it to a UUID
            value = UUID(value)
        uuid_as_str = str(value)
        return Expression.construct('cast({} as uuid)', Expression.string_value(uuid_as_str))

    @classmethod
    def dtype_to_expression(cls, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'uuid':
            return expression
        if source_dtype == 'string':
            # If the format is wrong, then this will give an error later on, but there is not much we can
            # do about that here.
            return Expression.construct('cast(({}) as uuid)', expression)
        # As far as we know the other types we support cannot be directly cast to uuid.
        raise ValueError(f'cannot convert {source_dtype} to uuid.')

    @classmethod
    def sql_gen_random_uuid(cls, base: DataFrameOrSeries) -> 'BuhTuhSeriesUuid':
        """
        Create a new Series object with for every row the `gen_random_uuid()` expression, which will
        evaluate to a random uuid for each row.

        Note that this is non-deterministic expression, it will give a different result each time it is run.
        This can have some unexpected consequences. Considers the following code:
            df['x'] = BuhTuhSeriesUuid.sql_gen_random_uuid(df)
            df['y'] = df['x']
            df['different'] = df['y'] != df['x']
        The df['different'] column will be True for all rows, because the second statement copies the
        unevaluated expression, not the result of the expression. So at evaluation time the expression will
        be evaluated twice for each row, for the 'x' column and the 'y' column, giving different results both
        times. One way to work around this is to materialize the dataframe in its current state (using
        get_df_materialized_model()), before adding any columns that reference a column that's created with
        this function.
        """
        return cls.get_class_instance(
            base=base,
            name='__tmp',
            expression=Expression.construct('gen_random_uuid()')
        )

    def _comparator_operator(self, other, comparator):
        other = const_to_series(base=self, value=other)
        self._check_supported(f"comparator '{comparator}'", ['uuid', 'string'], other)
        if other.dtype == 'uuid':
            expression = Expression.construct(f'({{}}) {comparator} ({{}})', self, other)
        else:
            expression = Expression.construct(f'({{}}) {comparator} (cast({{}} as uuid))', self, other)

        return self._get_derived_series('boolean', expression)
