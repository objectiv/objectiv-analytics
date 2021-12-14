"""
Copyright 2021 Objectiv B.V.
"""
from typing import Dict, Any, Union, Sequence, TypeVar

from bach.expression import Expression
from sql_models.util import quote_identifier
from sql_models.model import CustomSqlModel, SqlModel, SqlModelBuilder, SqlModelSpec, Materialization

TB = TypeVar('TB', bound='BachSqlModel')


class BachSqlModel(CustomSqlModel):

    def __call__(self: TB, **values: Union[int, str, Expression, Sequence[Expression],
                                           SqlModel, SqlModelBuilder]) -> SqlModel[TB]:
        """ Only add Expression types in signature """
        return super().__call__(**values)

    def set_values(self: TB, **values: Union[int, str, Expression, Sequence[Expression],
                                             SqlModel, SqlModelBuilder]) -> TB:
        """
        Set references that are required to resolve the entire model tree
        """
        for k, v in values.items():
            refs = []
            if isinstance(v, list) and all(isinstance(li, Expression) for li in v):
                refs = [value.get_references() for value in v]
            elif isinstance(v, Expression):
                refs = [v.get_references()]

            for r in refs:
                for rk, rv in r.items():
                    self._references[rk] = rv

        return super().set_values(**values)

    @staticmethod
    def properties_to_sql(properties: Dict[str, Any]) -> Dict[str, str]:
        """
        We accept Expressions and lists of expressions as properties too, and they need to escape
        themselves if they want to. This allows them to carry references that will be completed
        in the reference phase in _single_model_to_sql() from sql_generator.py
        """
        rv = {}
        for k, v in properties.items():
            if isinstance(v, list) and all(isinstance(li, Expression) for li in v):
                rv[k] = ", ".join([value.to_sql() for value in v])
            elif isinstance(v, Expression):
                rv[k] = v.to_sql()
            else:
                rv[k] = SqlModelSpec.escape_format_string(str(v))
        return rv


class SampleSqlModel(SqlModel):
    """
    A custom SqlModel that simply does select * from a table. In addition to that, this class stores an
    extra property: previous.

    The previous property is not used in the generated sql at all, but can be used to track a previous
    SqlModel. This is useful for how we implemented sampling, as that effectively insert a sql-model in the
    graph that has no regular reference to the previous node in the graph. By storing the previous node
    here, we can later still reconstruct what the actual previous node was with some custom logic.

    See the DataFrame.sample() implementation for more information
    """
    def __init__(self, table_name: str, previous: SqlModel, name: str = 'sample_node'):
        self.previous = previous
        sql = 'SELECT * FROM {table_name}'
        super().__init__(
            model_spec=CustomSqlModel(sql=sql, name=name),
            properties={'table_name': quote_identifier(table_name)},
            references={},
            materialization=Materialization.CTE
        )
