"""
Copyright 2021 Objectiv B.V.
"""
from typing import List, Dict, Union

from buhtuh import get_series_type_from_dtype, BuhTuhDataFrame
from buhtuh.expression import Expression


def get_fake_df(index_names: List[str], data_names: List[str], dtype: Union[str, Dict[str, str]] = 'int64'):
    engine = None,
    base_node = None,
    if isinstance(dtype, str):
        dtype = {
            col_name: dtype
            for col_name in index_names + data_names
        }

    index: Dict[str, 'BuhTuhSeries'] = {}
    for name in index_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        index[name] = series_type(
            engine=engine,
            base_node=base_node,
            index=None,
            name=name,
            expression=Expression.column_reference(name)
        )

    data: Dict[str, 'BuhTuhSeries'] = {}
    for name in data_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        data[name] = series_type(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=Expression.column_reference(name)
        )
    return BuhTuhDataFrame(engine=engine, base_node=base_node, index=index, series=data)


def get_fake_df_test_data() -> BuhTuhDataFrame:
    return get_fake_df(
        index_names=['_index_skating_order'],
        data_names=['skating_order', 'city', 'municipality', 'inhabitants', 'founding'],
        dtype={
            '_index_skating_order': 'int64',
            'skating_order': 'int64',
            'city': 'string',
            'municipality': 'string',
            'inhabitants': 'int64',
            'founding': 'int64'
        }
    )
