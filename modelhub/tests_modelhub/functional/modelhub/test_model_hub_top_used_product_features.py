"""
Copyright 2022 Objectiv B.V.
"""

# Any import from modelhub initializes all the types, do not remove
from modelhub import __version__
import pytest
from tests_modelhub.functional.modelhub.data_and_utils import get_objectiv_dataframe_test
from tests.functional.bach.test_data_and_utils import assert_equals_data


def test_top_used_product_features():
    df, modelhub = get_objectiv_dataframe_test()

    with pytest.raises(ValueError, match=f'The DataFrame has not all the necessary columns, '
                                         f'missing columns: feature_nice_name, application'):
        modelhub.aggregate.top_used_product_features(df)

    # adding the necessary columns
    df['application'] = df.global_contexts.gc.application
    df['feature_nice_name'] = df.location_stack.ls.nice_name

    tdf = modelhub.aggregate.top_used_product_features(df)

    # index checks
    assert len(tdf.index) == 3

    # index application
    assert_equals_data(
        tdf.index["application"],
        expected_columns=["application"],
        expected_data=[
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-website'],
            ['objectiv-docs'],
            ['objectiv-website'],
            ['objectiv-website']],
    )

    # index feature_nice_name
    assert "feature_nice_name" in tdf.index

    # index event_type
    assert set(tdf.index["event_type"].array) == {'ClickEvent'}

    # data info
    assert list(tdf.data.keys()) == ['user_id_nunique']
    assert set(tdf["user_id_nunique"].array) == {1}

