"""
Copyright 2021 Objectiv B.V.
"""
from sql_models.util import is_postgres
from tests.functional.bach.test_data_and_utils import get_df_with_json_data, assert_equals_data
import pytest

# We want to run all tests here for all supported databases, and thus we have the 'engine' argument on all
# tests. Or at least soon we'll have that, for now we use 'pg_engine'.
# Additionally, on Postgres we have two json dtypes: 'json' and 'jsonb' that should support the same
# operations. Therefore, we also have the 'dtype' argument. On all other databases than postgres we skip
# the tests for dtype 'jsonb' as those databases only support 'json'


pytestmark = [pytest.mark.parametrize('dtype', ('json', 'jsonb'))]


@pytest.fixture(autouse=True, scope='function')
def skip_jsonb_if_not_postgres(request):
    try:
        # TODO: remove this try-except when we support json on BigQuery and stop using 'pg_engine' here
        engine = request.getfixturevalue('engine')
    except pytest.FixtureLookupError:
        engine = request.getfixturevalue('pg_engine')
    if request.getfixturevalue('dtype') == 'jsonb' and not is_postgres(engine):
        pytest.skip(msg='jsonb dtype is only supported on Postgres. Skipping for other databases')


# TODO: BigQuery
def test_json_get_value(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    bts = bt.mixed_column.json.get_value('a')
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, "b"],
            [1, None],
            [2, "b"],
            [3, None]
        ]
    )


def test_json_get_single_value(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    a = bt.mixed_column[2]
    assert a == {'a': 'b', 'c': {'a': 'c'}}


def test_json_compare(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    bts = {"a": "b"} <= bt.mixed_column
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, True],
            [1, False],
            [2, True],
            [3, False]
        ]
    )
    bts = ["a"] <= bt.mixed_column
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, False],
            [1, True],
            [2, False],
            [3, False]
        ]
    )


def test_json_getitem(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    bts = bt.mixed_column.json[0]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, None],
            [1, "a"],
            [2, None],
            [3, {"_type": "WebDocumentContext", "id": "#document"}]
        ]
    )
    bts = bt.mixed_column.json[-2]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, None],
            [1, "c"],
            [2, None],
            [3, {"_type": "SectionContext", "id": "top-10"}]
        ]
    )
    bts = bt.mixed_column.json["a"]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'mixed_column'],
        expected_data=[
            [0, "b"],
            [1, None],
            [2, "b"],
            [3, None]
        ]
    )


def test_json_getitem_slice(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    bts = bt.list_column.json[1:]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, [{"c": "d"}]],
            [1, ["b", "c", "d"]],
            [2, [{"_type": "c", "id": "d"}, {"_type": "e", "id": "f"}]],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"},
                 {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    bts = bt.list_column.json[1:-1]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, None],
            [1, ["b", "c"]],
            [2, [{"_type": "c", "id": "d"}]],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"}]]
        ]
    )
    bts = bt.mixed_column.json[1:-1]
    with pytest.raises(Exception):  # slices only work on columns with only lists
        bts.head()


# tests below are for functions kind of specific to the objectiv (location) stack
def test_json_getitem_query(pg_engine, dtype):
    bt = get_df_with_json_data(engine=pg_engine, dtype=dtype)
    # if dict is contained in any of the dicts in the json list, the first index of the first match is
    # returned to the slice.
    bts = bt.list_column.json[{"_type": "SectionContext"}: ]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, None],
            [1, None],
            [2, None],
            [3, [{"_type": "SectionContext", "id": "home"}, {"_type": "SectionContext", "id": "top-10"},
                 {"_type": "ItemContext", "id": "5o7Wv5Q5ZE"}]]
        ]
    )
    bts = bt.list_column.json[1:{"id": "d"}]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, None],
            [1, None],
            [2, [{"_type": "c", "id": "d"}]],
            [3, None]
        ]
    )
    bts = bt.list_column.json[{'_type': 'a'}: {'id': 'd'}]
    assert_equals_data(
        bts,
        expected_columns=['_index_row', 'list_column'],
        expected_data=[
            [0, None],
            [1, None],
            [2, [{"_type": "a", "id": "b"}, {"_type": "c", "id": "d"}]],
            [3, None]
        ]
    )

    # TODO needs to_pandas() test
