"""
Copyright 2022 Objectiv B.V.
"""
from typing import Any, Tuple, TYPE_CHECKING, Dict, Optional, Mapping, Union

from sqlalchemy.engine import Dialect

from bach.series import Series
from bach.expression import Expression, join_expressions
from bach.types import DtypeOrAlias, get_series_type_from_dtype, StructuredDtype, Dtype, validate_dtype_value
from sql_models.constants import DBDialect
from sql_models.model import Materialization
from sql_models.util import DatabaseNotSupportedException, is_bigquery


if TYPE_CHECKING:
    from bach import DataFrameOrSeries


class SeriesDict(Series):
    """
    A Series that represents a dictionary-like type and its specific operations.
    On BigQuery this is backed by the STRUCT data type. On other databases this type is not supported.


    **instance_dtype:**
    An instance of this class expects an ``instance_dtype`` that's a dictionary. With each key being the
    name of a field, and the value being an instance-dtype describing that field. The values represented by
    such a Series must then be dictionaries with the exact same field names as the instance-dtype, and the
    specified data types for the fields.

    Example -
    BigQuery db_dtype: ``'STRUCT<a INT64, b ARRAY[FLOAT64], c <STRUCT x BOOL, y: INT64>>'``
    instance_dtype: ``{'a': 'int64', b: ['float64'], 'c': {'x': 'bool', 'y': 'int64'}``


    **Database support and types**

    * Postgres: not supported. Use :class:`SeriesJson` for similar functionality.
    * BigQuery: utilizes the 'STRUCT' database type.
    """
    dtype = 'dict'
    dtype_aliases: Tuple[DtypeOrAlias, ...] = tuple()
    supported_db_dtype = {
        # We support BigQuery STRUCT type, but the exact db_dtype depends on what kind of data the struct
        # holds (e.g. 'STRUCT<x INT64>'). So we don't define a static db_dtype that we support
        DBDialect.BIGQUERY: None
        # Postgres is not supported, thus not listed here
    }
    supported_value_types = (dict, )

    @classmethod
    def supported_literal_to_expression(cls, dialect: Dialect, literal: Expression) -> Expression:
        return literal

    @classmethod
    def supported_value_to_literal(
            cls,
            dialect: Dialect,
            value: Dict[str, Any],
            dtype: StructuredDtype
    ) -> Expression:
        # validate early, and help mypy
        cls.assert_engine_dialect_supported(dialect)
        if not isinstance(dtype, dict):
            raise ValueError(f'Dtype should be type dict. Type(dtype): {type(dtype)}')
        validate_dtype_value(static_dtype=cls.dtype, instance_dtype=dtype, value=value)

        sub_exprs = []
        for key, item in value.items():
            sub_dtype = dtype[key]
            series_type = get_series_type_from_dtype(sub_dtype)
            sub_val = series_type.value_to_expression(
                dialect=dialect,
                value=item,
                dtype=sub_dtype
            )
            sub_expr = Expression.construct('{} as {}', sub_val, Expression.identifier(key))
            sub_exprs.append(sub_expr)
        return Expression.construct('STRUCT({})', join_expressions(expressions=sub_exprs, join_str=', '))

    @classmethod
    def from_value(
        cls,
        base: 'DataFrameOrSeries',
        value: Dict[str, Any],
        name: str,
        dtype: Optional[StructuredDtype] = None
    ) -> 'SeriesDict':
        """
        Create an instance of this class, that represents a column with the given dict as value.
        The given base Series/DataFrame will be used to set the engine, base_node, and index.

        :param base:    The DataFrame or Series that the internal parameters are taken from
        :param value:   The value that this constant Series will have. Cannot be null.
        :param name:    The name that it will be known by (only for representation)
        :param dtype:   instance dtype, mandatory. Should be a dict, describing the structure of value.
        """
        # We override the parent class here to allow using Series as sub-values in a dict

        # validate early, and help mypy
        cls.assert_engine_dialect_supported(base.engine)
        if not isinstance(dtype, dict):
            raise ValueError(f'Dtype should be type dict. Type(dtype): {type(dtype)}')
        if value is None:
            raise ValueError(f'None values are not supported in from_value() by this class.')
        validate_dtype_value(static_dtype=cls.dtype, instance_dtype=dtype, value=value)

        sub_exprs = []
        for key, item in value.items():
            if isinstance(item, Series):
                if item.base_node != base.base_node:
                    raise ValueError(f'When constructing a struct from existing Series. '
                                     f'The Series.base_node must match the base.base_node. '
                                     f'Key with incorrect base-node: {key}')
                series = item
            else:
                sub_dtype = dtype[key]
                series_type = get_series_type_from_dtype(sub_dtype)
                series = series_type.from_value(
                    base=base,
                    value=item,
                    name=key,
                    dtype=sub_dtype
                )
            sub_expr = Expression.construct('{} as {}', series.expression, Expression.identifier(key))
            sub_exprs.append(sub_expr)
        expr = Expression.construct('STRUCT({})', join_expressions(expressions=sub_exprs, join_str=', '))
        result = cls.get_class_instance(
            engine=base.engine,
            base_node=base.base_node,
            index=base.index,
            name=name,
            expression=expr,
            group_by=None,
            order_by=[],
            instance_dtype=dtype
        )
        return result

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        # Even when casting from a dict to a dict, things will be troublesome if instance_dtype doesn't
        # match. So just raise an error.
        raise Exception('Cannot cast a value to a dictionary.')

    @property
    def elements(self) -> 'DictAccessor':
        """ Accessor to interact with the elements in the dictionary. """
        return DictAccessor(self)

    def materialize(
            self,
            node_name='manual_materialize',
            limit: Any = None,
            distinct: bool = False,
            materialization: Union[Materialization, str] = Materialization.CTE
    ):
        raise Exception(f'{self.__class__.__name__} cannot be materialized.')


class DictAccessor:
    def __init__(self, series: SeriesDict):
        self._series = series
        # Below checks on self._series.instance_dtype are not strictly needed, but it helps mypy. We checked
        # this in Series.__init__(), by calling validate_instance_dtype()
        if not isinstance(self._series.instance_dtype, dict):
            raise Exception('Found type: {self._series.instance_dtype}')
        self._instance_dtype: Dict[str, Any] = self._series.instance_dtype

    def __getitem__(self, key: str) -> 'Series':
        """
        Get an item from the dictionary.
        :param key: name of the field to get.
        """
        instance_dtype = self._instance_dtype
        if key not in instance_dtype:
            raise ValueError(f'Invalid key: {key}. '
                             f'Available keys: {sorted(instance_dtype.keys())}')
        expression = Expression.construct('{}.{}', self._series, Expression.identifier(key))
        sub_dtype = instance_dtype[key]
        if isinstance(sub_dtype, Dtype):
            new_dtype = sub_dtype
            return self._series \
                .copy_override_dtype(dtype=new_dtype) \
                .copy_override(expression=expression)
        elif isinstance(sub_dtype, dict):
            return self._series \
                .copy_override_type(SeriesDict, instance_dtype=sub_dtype) \
                .copy_override(expression=expression)
        elif isinstance(sub_dtype, list):
            from bach import SeriesList
            return self._series \
                .copy_override_type(SeriesList, instance_dtype=sub_dtype) \
                .copy_override(expression=expression)
        else:
            raise Exception(f'Unsupported structural type: {sub_dtype}')
