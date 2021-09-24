"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhSeries
from tests.functional.buhtuh.test_bt import get_bt_with_test_data, assert_equals_data


def test_string_slice():
    bt = get_bt_with_test_data()

    # Now try some slices
    for s in [slice(0, 3), slice(1, 3), slice(3, 3), slice(4, 3), slice(-4, -2), slice(-2, -2), slice(-2, 1)]:
        print(f'slice: {s}')
        bts = bt['city'].slice(s.start, s.stop)
        assert isinstance(bts, BuhTuhSeries)
        assert_equals_data(
            bts,
            expected_columns=['_index_skating_order', 'city'],
            expected_data=[
                [1, 'Ljouwert'.__getitem__(s)],
                [2, 'Snits'.__getitem__(s)],
                [3, 'Drylts'.__getitem__(s)]
            ]
        )

    # Some more with no beginnings or endings
    for s in [slice(None, 3), slice(3, None), slice(None, -3), slice(-3, None)]:
        print(f'slice: {s}')
        bts = bt['city'].slice(s.start, s.stop)
        assert isinstance(bts, BuhTuhSeries)
        assert_equals_data(
            bts,
            expected_columns=['_index_skating_order', 'city'],
            expected_data=[
                [1, 'Ljouwert'.__getitem__(s)],
                [2, 'Snits'.__getitem__(s)],
                [3, 'Drylts'.__getitem__(s)]
            ]
        )


def test_add_string_series():
    bt = get_bt_with_test_data()
    bts = bt['city'] + ' is in the municipality ' + bt['municipality']
    assert isinstance(bts, BuhTuhSeries)
    assert_equals_data(
        bts,
        expected_columns=['_index_skating_order', 'city'],
        expected_data=[
            [1, 'Ljouwert is in the municipality Leeuwarden'],
            [2, 'Snits is in the municipality Súdwest-Fryslân'],
            [3, 'Drylts is in the municipality Súdwest-Fryslân']
        ]
    )
