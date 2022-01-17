from bach.value_counts import ValueCounter
from tests.functional.bach.test_data_and_utils import get_bt_with_test_data
from tests.unit.bach.util import get_fake_df


def test_value_counts() -> None:
    df = get_fake_df(
        index_names=[],
        data_names=['a', 'b', 'c'],
        dtype={'a': 'string', 'b': 'integer', 'c': 'date'},
    )
    value_counter = ValueCounter(
        df=get_bt_with_test_data(full_data_set=True),
        subset=['inhabitants'],
        bins=2,
        normalize=True,
    )
    result = value_counter.get_value_counts()
