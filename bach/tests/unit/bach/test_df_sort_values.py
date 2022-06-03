"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from sql_models.util import is_postgres, is_bigquery
from tests.unit.bach.util import get_fake_df_test_data


def test_sort_values_wrong_parameters(dialect):
    bt = get_fake_df_test_data(dialect)
    with pytest.raises(KeyError):
        bt.sort_values('cityX')
    with pytest.raises(KeyError):
        bt.sort_values(['municipalityX', 'city'])
    with pytest.raises(TypeError):
        bt.sort_values({'municipality': False})
    with pytest.raises(ValueError):
        bt.sort_values(['municipality'], [False, True, True])
    with pytest.raises(ValueError):
        bt.sort_values(['municipality', 'city'], [False])


def test_generated_sql_order_last_select(dialect):
    # An earlier version of our code did include 'order by' statements, but not in the final select statement
    # This is not correct, but will often work and give a false sense of correctness.
    # The order by statement should be present in the final sql select. We test this by checking the last X
    # characters, this is a bit fragile but works okayish.
    bt = get_fake_df_test_data(dialect)
    sql_not_sorted = bt.view_sql()
    bt_sorted = bt.sort_values(by='city')
    sql_sorted = bt_sorted.view_sql()

    if is_postgres(dialect):
        expected_order_str = 'order by "city" asc'
    elif is_bigquery(dialect):
        expected_order_str = 'order by `city` asc'
    else:
        raise Exception(f'Need to expand test to support {dialect}')

    assert 'order by' not in sql_not_sorted[-60:]
    assert expected_order_str in sql_sorted[-60:]


def test_generated_sql_no_duplicate_sorting(dialect):
    # calling sort_values multiple times shouldn't result in multiple select statements being generated as
    # later sort statements cancel out earlier sort statements
    bt = get_fake_df_test_data(dialect)
    bt = bt.sort_values(by='city')
    first_sql = bt.view_sql()
    bt = bt.sort_values(by='municipality')
    bt = bt.sort_values(by='city')
    final_sql = bt.view_sql()
    assert first_sql == final_sql
