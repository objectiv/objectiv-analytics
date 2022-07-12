import numpy

from tests.functional.bach.test_data_and_utils import assert_equals_data, get_df_with_test_data


def test_from_const(engine):
    bt = get_df_with_test_data(engine)[['city']]
    bt['t'] = True
    bt['f'] = False
    assert_equals_data(
        bt.sort_index()[:1],
        expected_columns=['_index_skating_order', 'city', 't', 'f'],
        expected_data=[
            [1, 'Ljouwert', True, False],
        ]
    )


def test_to_pandas(engine):
    bt = get_df_with_test_data(engine)
    bt['t'] = True
    bt['f'] = False
    bt[['t', 'f']].to_pandas()
    numpy.testing.assert_array_equal(bt[['t', 'f']].to_numpy()[0], [True, False])

    
def test_operations(engine):
    bt = get_df_with_test_data(engine)[['city']]
    expected = []
    bt['t'] = True
    bt['f'] = False

    expected.extend([True, False])

    bt['and1'] = bt.t & bt.f
    bt['and2'] = bt.f & bt.t
    bt['and3'] = bt.t & bt.t
    bt['and4'] = bt.f & bt.f
    expected.extend([False, False, True, False])

    bt['or1'] = bt.t | bt.f
    bt['or2'] = bt.f | bt.t
    bt['or3'] = bt.t | bt.t
    bt['or4'] = bt.f | bt.f
    expected.extend([True, True, True, False])
    
    bt['xor1'] = bt.t ^ bt.f
    bt['xor2'] = bt.f ^ bt.t
    bt['xor3'] = bt.t ^ bt.t
    bt['xor4'] = bt.f ^ bt.f
    expected.extend([True, True, False, False])

    bt['inv1'] = ~bt.t
    bt['inv2'] = ~bt.f
    expected.extend([False, True])

    # this currently does not work as we cast to bigint, and that can not be casted back to bool
    # bt['int'] = 12
    # bt['int_astype'] = bt.int.astype('bool')
    # bt['int_and'] = bt.f & bt.int
    # bt['int_or'] = bt.f | bt.int
    # bt['int_xor'] = bt.f ^ bt.int
    # expected.extend([12, True, False, True, True])

    assert_equals_data(
        bt.sort_index()[:1],
        expected_columns=list(bt.all_series.keys()),
        expected_data=[
            [1, 'Ljouwert', *expected],
        ]
    )


def test_min_max(engine):
    df = get_df_with_test_data(engine)[['founding']]
    df['mixed'] = df['founding'] < 1400
    df['yes'] = True
    df['no'] = False
    assert_equals_data(
        df,
        expected_columns=['_index_skating_order', 'founding', 'mixed', 'yes', 'no'],
        expected_data=[
            [1, 1285, True, True, False],
            [2, 1456, False, True, False],
            [3, 1268, True, True, False]
        ]
    )
    assert_equals_data(
        df.min(),
        expected_columns=['founding_min', 'mixed_min', 'yes_min', 'no_min'],
        expected_data=[[1268, False, True, False]]
    )
    assert_equals_data(
        df.max(),
        expected_columns=['founding_max', 'mixed_max', 'yes_max', 'no_max'],
        expected_data=[[1456, True, True, False]]
    )
