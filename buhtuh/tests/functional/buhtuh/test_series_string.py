"""
Copyright 2021 Objectiv B.V.
"""
from buhtuh import BuhTuhSeries, BuhTuhSeriesString
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_from_const():
    a = 'a string'
    b = 'a string\'"\'\' "" \\ with quotes'
    c = None
    d = '\'\'!@&*(HJD☢'

    bt = get_bt_with_test_data()[['city']]
    bt['a'] = a
    bt['b'] = b
    bt['c'] = BuhTuhSeriesString.from_const(base=bt, value=c, name='temp')
    bt['d'] = BuhTuhSeriesString.from_const(base=bt, value=d, name='temp')
    assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'a', 'b', 'c', 'd'],
        expected_data=[
            [1, 'Ljouwert', a, b, c, d],
            [2, 'Snits', a, b, c, d],
            [3, 'Drylts', a, b, c, d]
        ]
    )


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
