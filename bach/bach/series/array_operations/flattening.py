from abc import ABC, abstractmethod
from typing import TypeVar, Dict, Tuple, cast

from bach.expression import Expression, join_expressions
from bach.sql_model import BachSqlModel, construct_references
from sql_models.model import CustomSqlModelBuilder, Materialization

from bach.series import SeriesJson, SeriesInt64

TSeriesJson = TypeVar('TSeriesJson', bound='SeriesJson')

_ITEM_IDENTIFIER_EXPR = Expression.identifier(name='__unnest_item')
_OFFSET_IDENTIFIER_EXPR = Expression.identifier(name='__unnest_item_offset')


class ArrayFlattening(ABC):
    """
    Abstract class that expands an array-type column into a set of rows.

    Child classes are in charge of specifying the correct expressions for unnesting arrays with
    the correct offset per each item.

    .. note::
        Final result will always have different base node than provided Series object.

    returns Tuple with:
        - SeriesJson: Representing the element of the array.
        - SeriesInt64: Offset of the element in the array
    """
    def __init__(self, series_object: 'TSeriesJson'):
        self._series_object = series_object.copy()

        if not self._series_object.is_materialized:
            self._series_object = cast(
                TSeriesJson, self._series_object.materialize(node_name='array_flatten')
            )

    def __call__(self, *args, **kwargs) -> Tuple['TSeriesJson', 'SeriesInt64']:
        from bach import DataFrame, SeriesInt64

        unnested_array_df = DataFrame.from_model(
            engine=self._series_object.engine,
            model=self._get_unnest_model(),
            index=list(self._series_object.index.keys()),
            all_dtypes=self.all_dtypes,
        )
        item_series = unnested_array_df[self.item_series_name]
        offset_series = unnested_array_df[self.item_offset_series_name]
        return (
            cast(TSeriesJson, item_series),
            offset_series.copy_override_type(SeriesInt64),
        )

    @property
    def item_series_name(self) -> str:
        """
        Final name of the series containing the array elements.
        """
        return self._series_object.name

    @property
    def item_offset_series_name(self) -> str:
        """
        Final name of the series containing the offset of the element in the array.
        """
        return f'{self._series_object.name}_offset'

    @property
    def all_dtypes(self) -> Dict[str, str]:
        """
        Mapping of all dtypes of all referenced columns in generated model
        """
        return {
            self.item_series_name: self._series_object.dtype,
            self.item_offset_series_name: 'int64',
            **{idx.name: idx.dtype for idx in self._series_object.index.values()}
        }

    def _get_unnest_model(self) -> BachSqlModel:
        """
        Creates a BachSqlModel in charge of expanding the array column.
        """
        column_expressions = self._get_column_expressions()
        select_column_expr = join_expressions(list(column_expressions.values()))
        from_model_expr = Expression.model_reference(self._series_object.base_node)
        cross_join_expr = self._get_cross_join_expression()

        sql_exprs = [select_column_expr, from_model_expr, cross_join_expr]
        dialect = self._series_object.engine.dialect
        sql = Expression.construct('SELECT {} FROM {} CROSS JOIN {}', *sql_exprs).to_sql(dialect)

        return BachSqlModel(
            model_spec=CustomSqlModelBuilder(sql=sql, name='unnest_array'),
            placeholders={},
            references=construct_references(base_references={}, expressions=sql_exprs),
            materialization=Materialization.CTE,
            materialization_name=None,
            column_expressions=column_expressions,
        )

    def _get_column_expressions(self) -> Dict[str, Expression]:
        """
        Final column expressions for the generated model
        """
        return {
            **{
                idx.name: idx.expression for idx in self._series_object.index.values()
            },
            self.item_series_name: Expression.construct_expr_as_name(
                expr=_ITEM_IDENTIFIER_EXPR, name=self.item_series_name
            ),
            self.item_offset_series_name: Expression.construct_expr_as_name(
                expr=_OFFSET_IDENTIFIER_EXPR, name=self.item_offset_series_name,
            ),
        }

    @abstractmethod
    def _get_cross_join_expression(self) -> Expression:
        """
        Expression that unnest/extract elements and offsets from array column. Later used
        in a cross join operation for joining the new set of rows back to the source.
        """
        raise NotImplementedError()


class BigQueryArrayFlattening(ArrayFlattening):
    def _get_cross_join_expression(self) -> Expression:
        """ For documentation, see implementation in class :class:`ArrayFlattening` """
        return Expression.construct(
            'UNNEST(JSON_QUERY_ARRAY({}.{})) AS {} WITH OFFSET AS {}',
            Expression.model_reference(self._series_object.base_node),
            self._series_object,
            _ITEM_IDENTIFIER_EXPR,
            _OFFSET_IDENTIFIER_EXPR,
        )


class PostgresArrayFlattening(ArrayFlattening):
    def _get_cross_join_expression(self) -> Expression:
        """ For documentation, see implementation in class :class:`ArrayFlattening` """
        return Expression.construct(
            'JSONB_ARRAY_ELEMENTS({}.{}) WITH ORDINALITY AS _unnested({}, {})',
            Expression.model_reference(self._series_object.base_node),
            self._series_object,
            _ITEM_IDENTIFIER_EXPR,
            _OFFSET_IDENTIFIER_EXPR,
        )

    def _get_column_expressions(self) -> Dict[str, Expression]:
        """
            Updates column expression for offset columns, since Postgres uses ordinality instead of offset.
        """
        column_expressions = super()._get_column_expressions()

        offset_expr = Expression.construct(
            '{} - 1 AS {}',
            _OFFSET_IDENTIFIER_EXPR,
            Expression.identifier(name=self.item_offset_series_name)
        )
        column_expressions[self.item_offset_series_name] = offset_expr
        return column_expressions
