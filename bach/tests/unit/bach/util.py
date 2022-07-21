"""
Copyright 2021 Objectiv B.V.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Union, cast, Any

import pandas
from sqlalchemy.engine import Dialect

from bach import get_series_type_from_dtype, DataFrame, Series
from bach.expression import Expression
from bach.savepoints import Savepoints
from bach.sql_model import BachSqlModel
from bach.types import StructuredDtype
from sql_models.model import CustomSqlModelBuilder


@dataclass(frozen=True)
class FakeEngine:
    """ Helper class that serves as a mock for SqlAlchemy Engine objects """
    dialect: Dialect
    name: str = field(init=False)
    url: str = 'postgresql://user@host:5432/db'

    def __post_init__(self):
        super().__setattr__('name', self.dialect.name)  # set the 'frozen' attribute self.name


class FakeSeries(Series):

    @classmethod
    def supported_value_to_literal(cls, dialect: Dialect, value: Any, dtype: StructuredDtype) -> Expression:
        pass

    @classmethod
    def dtype_to_expression(cls, dialect: Dialect, source_dtype: str, expression: Expression) -> Expression:
        pass

    def __lshift__(self, other) -> 'Series':
        pass

    def __rshift__(self, other) -> 'Series':
        pass

    def __invert__(self) -> 'Series':
        pass

    def __and__(self, other) -> 'Series':
        pass

    def __xor__(self, other) -> 'Series':
        pass

    def __or__(self, other) -> 'Series':
        pass


def get_fake_df(
    dialect: Dialect,
    index_names: List[str],
    data_names: List[str],
    dtype: Union[str, Dict[str, str]] = 'int64'
) -> DataFrame:
    engine = FakeEngine(dialect=dialect)
    column_names = index_names + data_names
    base_node = BachSqlModel.from_sql_model(
        sql_model=CustomSqlModelBuilder('select * from x', name='base')(),
        column_expressions={cn: Expression.column_reference(cn) for cn in column_names},
    )
    if isinstance(dtype, str):
        dtype = {
            col_name: dtype
            for col_name in index_names + data_names
        }

    index: Dict[str, 'Series'] = {}
    for name in index_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        index[name] = series_type(
            engine=engine,
            base_node=base_node,
            index={},
            name=name,
            expression=Expression.column_reference(name),
            group_by=cast('GroupBy', None),
            order_by=[],
            instance_dtype=series_type.dtype
        )

    data: Dict[str, 'Series'] = {}
    for name in data_names:
        series_type = get_series_type_from_dtype(dtype=dtype.get(name, 'int64'))
        data[name] = series_type(
            engine=engine,
            base_node=base_node,
            index=index,
            name=name,
            expression=Expression.column_reference(name),
            group_by=cast('GroupBy', None),
            order_by=[],
            instance_dtype=series_type.dtype
        )

    return DataFrame(engine=engine, base_node=base_node,
                     index=index, series=data, group_by=None, order_by=[], savepoints=Savepoints())


def get_fake_df_test_data(dialect: Dialect) -> DataFrame:
    return get_fake_df(
        index_names=['_index_skating_order'],
        data_names=['skating_order', 'city', 'municipality', 'inhabitants', 'founding'],
        dtype={
            '_index_skating_order': 'int64',
            'skating_order': 'int64',
            'city': 'string',
            'municipality': 'string',
            'inhabitants': 'int64',
            'founding': 'int64'
        },
        dialect=dialect
    )


def get_pandas_df(dataset: List[List[Any]], columns: List[str]) -> pandas.DataFrame:
    """
    Convert the given dataset to a Pandas DataFrame
    :param dataset: list, with each item representing a row, and each row consisting of a list of columns.
    :param columns: names of the columns
    """
    df = pandas.DataFrame.from_records(dataset, columns=columns)
    df.set_index(df.columns[0], drop=False, inplace=True)
    if 'moment' in df.columns:
        df['moment'] = df['moment'].astype('datetime64')
    if 'date' in df.columns:
        df['date'] = df['date'].astype('datetime64')
    return df
