"""
Copyright 2021 Objectiv B.V.
"""
from typing import Union, Optional
from uuid import UUID

from sqlalchemy.engine import Dialect

from bach import DataFrameOrSeries
from bach.series import Series, value_to_series
from bach.expression import Expression
from bach.series.series import WrappedPartition, ToPandasInfo
from bach.types import StructuredDtype
from sql_models.constants import DBDialect
from sql_models.util import is_postgres, DatabaseNotSupportedException, is_bigquery


class SeriesUuid(Series):
    """
    A Series that represents the UUID type and has UUID specific operations.

    **Database support and types**

    * Postgres: utilizes the native 'uuid' database type.
    * BigQuery: utilizes the generic 'STRING' database type.
    """
    dtype = 'uuid'
    dtype_aliases = ()
    supported_db_dtype = {
        DBDialect.POSTGRES: 'uuid',
        # None here for BIGQUERY, because BigQuery doesn't have a uuid type.
        # We do support the UUID Series, but on BQ we store data as STRING data-type, which by default is
        # handled by SeriesString
        DBDialect.BIGQUERY: None
    }

    supported_value_types = (UUID, str)

    @classmethod
    def get_db_dtype(cls, dialect: Dialect) -> Optional[str]:
        if not is_bigquery(dialect):
            return super().get_db_dtype(dialect)

        from bach.series import SeriesString
        return SeriesString.get_db_dtype(dialect)

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
        value: Union[UUID, str],
        dtype: StructuredDtype
    ) -> Expression:
        if isinstance(value, str):
            # Check that the string value is a valid UUID by converting it to a UUID
            value = UUID(value)
        uuid_as_str = str(value)
        return Expression.string_value(uuid_as_str)

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        if source_dtype == 'uuid':
            return expression
        if source_dtype == 'string':
            if is_postgres(dialect):
                # If the format is wrong, then this will give an error later on, but there is not much we can
                # do about that here.
                return Expression.construct(f'cast({{}} as {cls.get_db_dtype(dialect)})', expression)
            if is_bigquery(dialect):
                return expression
            raise DatabaseNotSupportedException(dialect)
        # As far as we know the other types we support cannot be directly cast to uuid.
        raise ValueError(f'cannot convert {source_dtype} to uuid.')

    @classmethod
    def random(cls, base: DataFrameOrSeries) -> 'SeriesUuid':
        """
        Create a new Series object with an expression, that will evaluate to a random uuid for each row.

        :param base: DataFrame or Series from which the newly created Series' engine, base_node and index
            parameters are copied.

        .. warning::
            The returned Series has a non-deterministic expression, it will give a different result each
            time it is evaluated by the database.

        The non-deterministic expression can have some unexpected consequences. Consider the following code:

        .. code-block:: python

            df['x'] = SeriesUuid.random(df)
            df['y'] = df['x']
            df['different'] = df['y'] != df['x']

        The df['different'] series will be True for all rows, because the second statement copies the
        unevaluated expression, not the result of the expression. So at evaluation time the expression will
        be evaluated twice for each row, for the 'x' column and the 'y' column, giving different results both
        times. One way to work around this is to materialize the dataframe in its current state (using
        materialize()), before adding any columns that reference a column that's created with
        this function.
        """
        if is_postgres(base.engine):
            expr_str = 'gen_random_uuid()'
        elif is_bigquery(base.engine):
            expr_str = 'GENERATE_UUID()'
        else:
            raise DatabaseNotSupportedException(base.engine)
        return cls.get_class_instance(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name='random',
            expression=Expression.construct(expr_str),
            group_by=None,
            order_by=[],
            instance_dtype=cls.dtype
        )

    def to_pandas_info(self) -> Optional[ToPandasInfo]:
        if is_bigquery(self.engine):
            return ToPandasInfo('object', UUID)
        return None

    def _comparator_operation(self, other, comparator, other_dtypes=('uuid', 'string')):
        from bach import SeriesBoolean
        other = value_to_series(base=self, value=other)
        self_modified, other = self._get_supported(f"comparator '{comparator}'", other_dtypes, other)
        if other.dtype == 'string' and is_postgres(self.engine):
            expression = Expression.construct(
                f'({{}}) {comparator} (cast({{}} as uuid))', self_modified, other
            )
        else:  # other.dtype == 'uuid' or not is_postgres(self.engine)
            expression = Expression.construct(f'({{}}) {comparator} ({{}})', self_modified, other)
        return self_modified.copy_override_type(SeriesBoolean).copy_override(expression=expression)

    def min(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()

    def max(self, partition: WrappedPartition = None, skipna: bool = True):
        """ INTERNAL: Only here to not trigger errors from describe """
        raise NotImplementedError()
