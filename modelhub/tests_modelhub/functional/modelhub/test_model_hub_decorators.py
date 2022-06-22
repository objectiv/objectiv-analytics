from tests_modelhub.data_and_utils.utils import get_objectiv_dataframe_test


def test_compare_decorator_limiting(db_params, monkeypatch) -> None:
    df, modelhub = get_objectiv_dataframe_test(db_params, time_aggregation='%Y-%m-%d')
    # add conversion event
    modelhub.add_conversion_event(
        location_stack=df.location_stack.json[{'_type': 'LinkContext', 'id': 'cta-repo-button'}:],
        event_type='ClickEvent',
        name='github_clicks',
    )

    decorated_pch = modelhub.map.pre_conversion_hit_number(df, 'github_clicks')

    monkeypatch.setattr(
        'modelhub.decorators._get_extra_series_to_include_from_params',
        lambda *args, **kwargs: df.columns,
    )
    mocked_decorated_pch = modelhub.map.pre_conversion_hit_number(df, 'github_clicks')

    # final result must be the same
    assert decorated_pch.base_node.sql == mocked_decorated_pch.base_node.sql

    # result from materialization of __conversions max window function
    dec_prev_node = decorated_pch.base_node.references['prev']
    mocked_dec_prev_node = mocked_decorated_pch.base_node.references['prev']
    assert len(dec_prev_node.column_expressions) == 7
    assert len(mocked_dec_prev_node.column_expressions) == 12

    # result from materialization from merge when adding conversions in time
    dec_prev_node = dec_prev_node.references['prev']
    mocked_dec_prev_node = mocked_dec_prev_node.references['prev']
    assert len(dec_prev_node.column_expressions) == 6
    assert len(mocked_dec_prev_node.column_expressions) == 11

    # initial df
    dec_prev_node = dec_prev_node.references['left_node']
    mocked_dec_prev_node = mocked_dec_prev_node.references['left_node']
    assert dec_prev_node == df.base_node
    assert mocked_dec_prev_node == df.base_node
    assert len(dec_prev_node.column_expressions) == len(df.base_node.column_expressions)
    assert len(mocked_dec_prev_node.column_expressions) == len(df.base_node.column_expressions)
