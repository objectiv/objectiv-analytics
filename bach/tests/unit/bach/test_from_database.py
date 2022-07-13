"""
Copyright 2022 Objectiv B.V.
"""
from bach.from_database import _get_meta_data_table_from_table_name


def test__get_meta_data_table_from_table_name():
    assert _get_meta_data_table_from_table_name('test_table') == ('INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_meta_data_table_from_table_name('dataset.test_table') == \
           ('dataset.INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_meta_data_table_from_table_name('project_id.dataset.test_table') == \
           ('project_id.dataset.INFORMATION_SCHEMA.COLUMNS', 'test_table')
    assert _get_meta_data_table_from_table_name('objectiv-production.a-dataset.a_table') == \
           ('objectiv-production.a-dataset.INFORMATION_SCHEMA.COLUMNS', 'a_table')
