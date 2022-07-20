"""
Copyright 2021 Objectiv B.V.
"""
import pytest

from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_reset_index_to_empty(engine):
    bt = get_df_with_test_data(engine)
    assert list(bt.index.keys()) == ['_index_skating_order']
    assert '_index_skating_order' not in bt.data

    # regular
    rbt = bt.reset_index()
    assert list(rbt.index.keys()) == []
    assert '_index_skating_order' in rbt.data

    # drop
    dbt = bt.reset_index(drop=True)
    assert list(dbt.index.keys()) == []
    assert '_index_skating_order' not in dbt.data

    for r in [bt, rbt, dbt]:
        for s in r.index.values():
            assert(s.index == {})
        for s in r.data.values():
            assert(s.index == r.index)
        r.head()

    bt_cp = bt.copy()
    bt_cp = bt_cp.set_index(['skating_order', 'city'], append=True)
    final_index = ['_index_skating_order', 'skating_order']
    # level
    lbt = bt_cp.reset_index(level='city')
    assert 'city' in lbt.data
    assert list(lbt.index.keys()) == final_index

    # level + drop
    lbt = bt_cp.reset_index(level='city', drop=True)
    assert 'city' not in lbt.data
    assert list(lbt.index.keys()) == final_index

    # dropping invalid level
    invalid_level = 'random'
    with pytest.raises(ValueError, match=fr"'{invalid_level}' level not found"):
        bt_cp.reset_index(level=['city', invalid_level])


def test_reset_index_materialize(engine):
    bt = get_df_with_test_data(engine)[['municipality', 'inhabitants']]
    assert list(bt.index.keys()) == ['_index_skating_order']

    bt = bt.groupby('municipality').sum()
    assert list(bt.index.keys()) == ['municipality']

    # regular, materializes automatically
    rbt = bt.reset_index()
    assert list(bt.index.keys()) == ['municipality']
    assert list(rbt.index.keys()) == []

    for r in [bt, rbt]:
        for s in r.index.values():
            assert(s.index == {})
        for s in r.data.values():
            assert(s.index == r.index)

        assert_equals_data(
            r,
            expected_columns=[
                'municipality', 'inhabitants_sum'
            ],
            expected_data=[
                ['Leeuwarden', 93485],
                ['Súdwest-Fryslân', 36575],
            ],
            order_by=['municipality'],
        )
