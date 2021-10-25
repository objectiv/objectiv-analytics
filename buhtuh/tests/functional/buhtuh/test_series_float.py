# TODO maybe combine this with int into numeric series tests?
# TODO test basics
# TODO test type conversions
# TODO test aggregation functions
import math
from unittest.mock import ANY

from buhtuh import BuhTuhSeriesFloat64
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, assert_equals_data


def test_from_const():
    a = 123.45
    b = -123.45
    c = -0.0
    d = float('nan')
    e = float('infinity')
    f = float('-infinity')
    g = None

    bt = get_bt_with_test_data()[['city']]
    bt['a'] = a
    bt['b'] = b
    bt['c'] = c
    bt['d'] = d
    bt['e'] = e
    bt['f'] = f
    bt['g'] = BuhTuhSeriesFloat64.from_const(base=bt, value=g, name='tmp')
    # check column d separately as `nan == nan` always evaluates to False
    db_values = assert_equals_data(
        bt,
        expected_columns=['_index_skating_order', 'city', 'a', 'b', 'c', 'd', 'e', 'f', 'g'],
        expected_data=[
            [1, 'Ljouwert', a, b, c, ANY, e, f, g],
            [2, 'Snits', a, b, c, ANY, e, f, g],
            [3, 'Drylts', a, b, c, ANY, e, f, g]
        ]
    )
    for row in db_values:
        assert math.isnan(row[5])
