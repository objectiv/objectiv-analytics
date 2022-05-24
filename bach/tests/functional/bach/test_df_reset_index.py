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


def test_set_index(engine):
    bt = get_df_with_test_data(engine)[['municipality', 'city', 'inhabitants']]
    assert list(bt.index.keys()) == ['_index_skating_order']

    # regular reset in different ways
    sbt = bt.set_index(keys=[], drop=False)
    rbt = bt.reset_index(drop=True)
    assert list(rbt.index.keys()) == []
    assert list(sbt.index.keys()) == []
    assert '_index_skating_order' not in sbt.data
    assert '_index_skating_order' not in rbt.data
    sbt.head()  # check valid sql /df conversion
    rbt.head()

    # regular set
    with pytest.raises(ValueError,
                       match="When adding existing series to the index, drop must be True"):
        bt.set_index(keys=['municipality'], drop=False)

    sbt = bt.set_index(['municipality'], drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']
    sbt.head()  # check valid sql

    # set to existing changes nothing
    sbt = bt.set_index(['municipality'], drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']
    nbt = sbt.set_index(['municipality'], drop=True)
    assert list(nbt.index.keys()) == ['municipality']
    assert list(nbt.data.keys()) == ['city', 'inhabitants']
    nbt.head()  # check valid sql

    # appending index without drop raises
    with pytest.raises(ValueError,
                       match="When adding existing series to the index, drop must be True"):
        sbt = bt.set_index(['municipality'], drop=True)
        sbt.set_index(['city'], append=True, drop=False)

    sbt = bt.set_index(['municipality'], drop=True)
    abt = sbt.set_index(['city'], append=True, drop=True)
    assert list(abt.index.keys()) == ['municipality', 'city']
    assert list(abt.data.keys()) == ['inhabitants']
    abt.head()  # check valid sql

    # try to remove a series
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['city'], drop=False)
    assert list(rbt.index.keys()) == ['city']
    assert list(rbt.data.keys()) == ['inhabitants']
    rbt.head()

    # try to remove a series with drop
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['city'], drop=True)
    assert list(rbt.index.keys()) == ['city']
    assert list(rbt.data.keys()) == ['inhabitants']
    rbt.head()

    # try to remove a series from the other end
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['municipality'], drop=False)
    assert list(rbt.index.keys()) == ['municipality']
    assert list(rbt.data.keys()) == ['inhabitants']
    rbt.head()

    # try to remove a series from the other end with drop
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['municipality'], drop=True)
    assert list(rbt.index.keys()) == ['municipality']
    assert list(rbt.data.keys()) == ['inhabitants']
    rbt.head()

    # try to set a series as index
    sbt = bt.set_index(bt.municipality, drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']
    sbt.head()

    # use a series with a unique name, should work without drop
    col = bt.city
    abt = bt.rename(columns={'city': 'x'})
    xbt = abt.set_index(col, drop=False)
    assert list(xbt.index.keys()) == ['city']
    assert list(xbt.data.keys()) == ['municipality', 'x', 'inhabitants']

    # try to set a series as index
    abt = bt.set_index(bt.municipality.str[:3], drop=True)
    assert list(abt.index.keys()) == ['municipality']
    assert list(abt.data.keys()) == ['city', 'inhabitants']
    abt.head()


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
                'municipality', '_index_skating_order_sum', 'inhabitants_sum'
            ],
            expected_data=[
                ['Leeuwarden', 1, 93485],
                ['Súdwest-Fryslân', 5, 36575],
            ],
            order_by=['_index_skating_order_sum'],
        )