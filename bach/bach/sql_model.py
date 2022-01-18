"""
Copyright 2021 Objectiv B.V.
"""
import typing
from typing import Dict, TypeVar, Tuple, List, Optional, Mapping, Hashable

from bach.expression import Expression, get_variable_tokens, VariableToken
from bach.types import value_to_dtype, get_series_type_from_dtype
from sql_models.util import quote_identifier
from sql_models.model import CustomSqlModelBuilder, SqlModel, SqlModelSpec, Materialization

T = TypeVar('T', bound='SqlModelSpec')


if typing.TYPE_CHECKING:
    from bach.dataframe import DtypeNamePair


class BachSqlModel(SqlModel[T]):
    """
    SqlModel with meta information about the columns that it produces.
    This additional information needs to be specifically set at model instantiation, it cannot be deduced
    from the sql.

    The column information is not used for sql generation, but can be used by other code
    interacting with the models. The information is not reflected in the `hash`, as it doesn't matter for
    the purpose of sql generation.
    """
    def __init__(self,
                 model_spec: T,
                 properties: Mapping[str, Hashable],
                 references: Mapping[str, 'SqlModel'],
                 materialization: Materialization,
                 materialization_name: Optional[str],
                 columns: Tuple[str, ...]
                 ):
        """
        Similar to :py:meth:`SqlModel.__init__()`. With one additional parameter: columns, the names of the
        columns that this model's query will return in the correct order.
        """
        self._columns = columns
        super().__init__(
            model_spec=model_spec,
            properties=properties,
            references=references,
            materialization=materialization,
            materialization_name=materialization_name)

    @property
    def columns(self) -> Tuple[str, ...]:
        """ Columns returned by the query of this model, in order."""
        return self._columns

    @classmethod
    def from_sql_model(cls, sql_model: SqlModel, columns: Tuple[str, ...]) -> 'BachSqlModel':
        """ From any SqlModel create a BachSqlModel with the given column definitions. """
        return cls(
            model_spec=sql_model.model_spec,
            properties=sql_model.properties,
            references=sql_model.references,
            materialization=sql_model.materialization,
            materialization_name=sql_model.materialization_name,
            columns=columns
        )


class SampleSqlModel(BachSqlModel):
    """
    A custom SqlModel that simply does select * from a table. In addition to that, this class stores an
    extra property: previous.

    The previous property is not used in the generated sql at all, but can be used to track a previous
    SqlModel. This is useful for how we implemented sampling, as that effectively inserts a sql-model in the
    graph that has no regular reference to the previous node in the graph. By storing the previous node
    here, we can later still reconstruct what the actual previous node was with some custom logic.

    See the DataFrame.sample() implementation for more information
    """
    def __init__(self,
                 table_name: str,
                 previous: SqlModel,
                 columns: Tuple[str, ...],
                 name: str = 'sample_node'):
        self.previous = previous
        sql = 'SELECT * FROM {table_name}'
        super().__init__(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            properties={'table_name': quote_identifier(table_name)},
            references={},
            materialization=Materialization.CTE,
            materialization_name=None,
            columns=columns
        )


class CurrentNodeSqlModel(BachSqlModel):
    def __init__(self, *,
                 name: str,
                 column_names: Tuple[str, ...],
                 column_exprs: List[Expression],
                 where_clause: Optional[Expression],
                 group_by_clause: Optional[Expression],
                 having_clause: Optional[Expression],
                 order_by_clause: Optional[Expression],
                 limit_clause: Expression,
                 previous_node: BachSqlModel,
                 variables: Dict['DtypeNamePair', Hashable]):

        columns_str = ', '.join(expr.to_sql() for expr in column_exprs)
        where_str = where_clause.to_sql() if where_clause else ''
        group_by_str = group_by_clause.to_sql() if group_by_clause else ''
        having_str = having_clause.to_sql() if having_clause else ''
        order_by_str = order_by_clause.to_sql() if order_by_clause else ''
        limit_str = limit_clause.to_sql() if limit_clause else ''

        sql = (
            f"select {columns_str} \n"
            f"from {{{{prev}}}} \n"
            f"{where_str} \n"
            f"{group_by_str} \n"
            f"{having_str} \n"
            f"{order_by_str} \n"
            f"{limit_str} \n"
        )

        # Add all references found in the Expressions to self.references
        nullable_expressions = [where_clause, group_by_clause, having_clause, order_by_clause, limit_clause]
        all_expressions = column_exprs + [expr for expr in nullable_expressions if expr is not None]
        references = construct_references({'prev': previous_node}, all_expressions)

        # Set all relevant variables as properties
        filtered_variables = filter_variables(variables, all_expressions)
        properties = get_variable_values_sql(filtered_variables)

        super().__init__(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            properties=properties,
            references=references,
            materialization=Materialization.CTE,
            materialization_name=None,
            columns=column_names
        )


def construct_references(
        base_references: Mapping[str, 'SqlModel'],
        expressions: List['Expression']
) -> Dict[str, 'SqlModel']:
    """
    Create a dictionary of references consisting of the base_references and all references found in the
    expressions.

    Will raise an exception if there are references with the same name that reference different models.
    """
    result: Dict[str, SqlModel] = {}
    for expr in expressions:
        references = expr.get_references()
        _check_reference_conflicts(result, references)
        result.update(references)
    _check_reference_conflicts(base_references, result)
    result.update(base_references)
    return result


def _check_reference_conflicts(left: Mapping[str, 'SqlModel'], right: Mapping[str, 'SqlModel']) -> None:
    """
    Util function: Check that two dicts with references don't have conflicting values.
    """
    for ref_name, model in right.items():
        if left.get(ref_name) not in (None, model):
            # This should never happen, if other code doesn't mess up.
            # We have this check as a backstop assertion to fail early
            raise Exception(f'Encountered reference {ref_name} before, but with a different value: '
                            f'{left.get(ref_name)} != {model}')


def filter_variables(
        variable_values: Dict['DtypeNamePair', Hashable],
        filter_expressions: List['Expression']
) -> Dict['DtypeNamePair', Hashable]:
    """
    Util function: Return a copy of the variable_values, with only the variables for which there is a
    VariableToken in the filter_expressions.
    """
    available_tokens = get_variable_tokens(filter_expressions)
    dtype_names = {token.dtype_name for token in available_tokens}

    return {dtype_name: value for dtype_name, value in variable_values.items() if dtype_name in dtype_names}


def get_variable_values_sql(variable_values: Dict['DtypeNamePair', Hashable]) -> Dict[str, str]:
    """
    Take a dictionary with variable_values and return a dict with the full variable names and the values
    as sql.
    The sql assumes it will be used as values for SqlModels's placeholders. i.e. It will not be format
    escaped, unlike if it would be used directly into SqlModel.sql in which case it would be escaped twice.

    :param variable_values: Mapping of variable to value.
    :return: Dictionary mapping full variable name to sql literal
    """
    result = {}
    for dtype_name, value in variable_values.items():
        dtype, name = dtype_name
        value_dtype = value_to_dtype(value)
        if dtype != value_dtype:  # should never happen
            Exception(f'Dtype of value {value}, {value_dtype} does not match registered dtype {dtype}')
        property_name = VariableToken.dtype_name_to_property_name(dtype=dtype, name=name)
        series_type = get_series_type_from_dtype(dtype)
        expr = series_type.supported_value_to_literal(value)
        double_escaped_sql = expr.to_sql()
        sql = double_escaped_sql.format().format()
        result[property_name] = sql
    return result
