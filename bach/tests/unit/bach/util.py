"""
Copyright 2021 Objectiv B.V.
"""
from typing import List, Dict, Union, cast

from bach import get_series_type_from_dtype, DataFrame
from bach.expression import Expression
from bach.savepoints import Savepoints


def get_fake_df(index_names: List[str], data_names: List[str], dtype: Union[str, Dict[str, str]] = 'int64'):
    engine = None
    base_node = None
    if isinstance(dtype, str):
        dtype = {
            col_name: dtype
            for col_name in index_names + data_names
        }

    index: Dict[str, 'Series'] = {}
    for name in index_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        index[name] = series_type(
            engine=engine,
            base_node=base_node,
            index={},
            name=name,
            expression=Expression.column_reference(name),
            group_by=cast('GroupBy', None)
        )

    data: Dict[str, 'Series'] = {}
    for name in data_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        data[name] = series_type(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=Expression.column_reference(name),
            group_by=cast('GroupBy', None))

    return DataFrame(engine=engine, base_node=base_node,
                     index=index, series=data, group_by=None, order_by=[], savepoints=Savepoints())


def get_fake_df_test_data() -> DataFrame:
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
