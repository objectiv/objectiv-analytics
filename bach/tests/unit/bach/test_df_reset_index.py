"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from tests.unit.bach.util import get_fake_df_test_data


def test_reset_index_no_change(dialect):
    bt = get_fake_df_test_data(dialect)
    bt = bt.set_index(['skating_order', 'city'], append=True)
    lbt = bt.reset_index(level=[])
    assert list(lbt.index.keys()) == list(bt.index.keys())


def test_set_index(dialect):
    bt = get_fake_df_test_data(dialect)[['municipality', 'city', 'inhabitants']]
    assert list(bt.index.keys()) == ['_index_skating_order']

    # regular reset in different ways
    sbt = bt.set_index(keys=[], drop=False)
    rbt = bt.reset_index(drop=True)
    assert list(rbt.index.keys()) == []
    assert list(sbt.index.keys()) == []
    assert '_index_skating_order' not in sbt.data
    assert '_index_skating_order' not in rbt.data

    # regular set
    with pytest.raises(ValueError,
                       match="When adding existing series to the index, drop must be True"):
        bt.set_index(keys=['municipality'], drop=False)

    sbt = bt.set_index(['municipality'], drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']

    # set to existing changes nothing
    sbt = bt.set_index(['municipality'], drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']
    nbt = sbt.set_index(['municipality'], drop=True)
    assert list(nbt.index.keys()) == ['municipality']
    assert list(nbt.data.keys()) == ['city', 'inhabitants']

    # appending index without drop raises
    with pytest.raises(ValueError,
                       match="When adding existing series to the index, drop must be True"):
        sbt = bt.set_index(['municipality'], drop=True)
        sbt.set_index(['city'], append=True, drop=False)

    sbt = bt.set_index(['municipality'], drop=True)
    abt = sbt.set_index(['city'], append=True, drop=True)
    assert list(abt.index.keys()) == ['municipality', 'city']
    assert list(abt.data.keys()) == ['inhabitants']

    # try to remove a series
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['city'], drop=False)
    assert list(rbt.index.keys()) == ['city']
    assert list(rbt.data.keys()) == ['inhabitants']
    # try to remove a series with drop
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['city'], drop=True)
    assert list(rbt.index.keys()) == ['city']
    assert list(rbt.data.keys()) == ['inhabitants']

    # try to remove a series from the other end
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['municipality'], drop=False)
    assert list(rbt.index.keys()) == ['municipality']
    assert list(rbt.data.keys()) == ['inhabitants']

    # try to remove a series from the other end with drop
    abt = bt.set_index(['city', 'municipality'], drop=True)
    rbt = abt.set_index(['municipality'], drop=True)
    assert list(rbt.index.keys()) == ['municipality']
    assert list(rbt.data.keys()) == ['inhabitants']

    # try to set a series as index
    sbt = bt.set_index(bt.municipality, drop=True)
    assert list(sbt.index.keys()) == ['municipality']
    assert list(sbt.data.keys()) == ['city', 'inhabitants']

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
