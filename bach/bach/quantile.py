from typing import cast, Union, List

from bach import SeriesString
from bach.series import SeriesAbstractNumeric, SeriesTimedelta, Series
from bach.expression import Expression, AggregateFunctionExpression, WindowFunctionExpression
from bach.series.series import WrappedPartition
from sql_models.util import is_bigquery


def calculate_quantiles(
    series: Union[SeriesTimedelta, SeriesAbstractNumeric],
    partition: WrappedPartition = None,
    q: Union[float, List[float]] = 0.5,
) -> Series:
    """
    When q is a float or len(q) == 1, the resultant series index will remain
    In case multiple quantiles are calculated, the resultant series index will have all calculated
    quantiles as index values.
    """
    quantiles = [q] if isinstance(q, float) else q
    quantile_results = []

    partition = partition or series.group_by
    #  BigQuery requires a window function for quantiles, window frame clause is not allowed
    window = None
    if is_bigquery(series.engine):
        from bach.partitioning import Window, GroupBy
        group_by = None
        if partition:
            group_by = partition if isinstance(partition, GroupBy) else partition.group_by
        window = Window(
            group_by_columns=list(group_by.index.values()) if group_by else [],
            order_by=[],
            start_boundary=None,
            end_boundary=None,
        )

    for qt in quantiles:
        if qt < 0 or qt > 1:
            raise ValueError(f'value {qt} should be between 0 and 1.')

        if is_bigquery(series.engine):
            # BigQuery names should start with a letter or underscore. Dots are not valid
            q_col_name = f"__q_{str(qt).replace('.', '_')}"
            agg_result = series.copy_override(name=q_col_name)._derived_agg_func(
                partition=window,
                expression=Expression.construct(f'percentile_cont({{}}, {qt})', series),
                dtype='float64',
            )
        else:
            agg_result = series.copy_override(name=str(qt))._derived_agg_func(
                partition=partition,
                expression=AggregateFunctionExpression.construct(
                    f'percentile_cont({qt}) within group (order by {{}})', series,
                ),
            )

        quantile_results.append(agg_result)

    base_q = quantile_results[0]
    if len(quantile_results) == 1:
        return base_q

    df = base_q.to_frame().copy_override(series={s.name: s for s in quantile_results})
    # stack all series into one. q values are in index
    # should keep q index since multiple quantiles were calculated
    final_index = (df.index_columns if partition else []) + ['q']
    df = df.stack().to_frame()
    df = df.reset_index(drop=False).rename(columns={'__stacked_index': 'q', '__stacked': series.name})
    df = df[final_index + [series.name]]

    if is_bigquery(series.engine):
        # TODO: replace with df['q'].str[2:].str.replace('_', '.') when supported
        df['q'] = df['q'].copy_override(
            expression=Expression.construct(
                f"replace({{}}, '_', '.')",
                df['q'].copy_override_type(SeriesString).str[4:],
            ),
        )

        # BigQuery returns quantile per row, need to apply distinct
        df = df.materialize(node_name='quantile', distinct=True)

    # q values should be numeric
    df['q'] = df['q'].astype(float)
    return df.set_index(final_index)[series.name]
