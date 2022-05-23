"""
Copyright 2021 Objectiv B.V.
"""
import typing
from typing import Dict, TypeVar, Tuple, List, Optional, Mapping, Hashable, Union

from sqlalchemy.engine import Dialect

from bach.expression import Expression, get_variable_tokens, VariableToken
from bach.types import value_to_dtype, get_series_type_from_dtype
from sql_models.util import quote_identifier
from sql_models.model import CustomSqlModelBuilder, SqlModel, Materialization, SqlModelSpec
from sql_models.constants import NotSet, not_set

T = TypeVar('T', bound='SqlModelSpec')
TBachSqlModel = TypeVar('TBachSqlModel', bound='BachSqlModel')


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
    def __init__(
        self,
        model_spec: T,
        placeholders: Mapping[str, Hashable],
        references: Mapping[str, 'SqlModel'],
        materialization: Materialization,
        materialization_name: Optional[str],
        column_expressions: Dict[str, Expression],
    ) -> None:
        """
        Similar to :py:meth:`SqlModel.__init__()`. With one additional parameter: column_expressions,
        a mapping between the names of the columns and expressions
        that this model's query will return in the correct order.
        """
        self._column_expressions = column_expressions
        super().__init__(
            model_spec=model_spec,
            placeholders=placeholders,
            references=references,
            materialization=materialization,
            materialization_name=materialization_name,
        )

    @property
    def columns(self) -> Tuple[str, ...]:
        """ Columns returned by the query of this model, in order."""
        return tuple(self._column_expressions.keys())

    @property
    def column_expressions(self) -> Dict[str, Expression]:
        """ Mapping containing the expression used per column."""
        return self._column_expressions

    def copy_override(
        self: TBachSqlModel,
        *,
        model_spec: T = None,
        placeholders: Mapping[str, Hashable] = None,
        references: Mapping[str, 'SqlModel'] = None,
        materialization: Materialization = None,
        materialization_name: Union[Optional[str], NotSet] = not_set,
        column_expressions: Dict[str, Expression] = None
    ) -> TBachSqlModel:
        """
        Similar to super class's implementation, but adds optional 'columns' parameter
        """
        materialization_name_value = (
            self.materialization_name if materialization_name is not_set else materialization_name
        )
        return self.__class__(
            model_spec=self.model_spec if model_spec is None else model_spec,
            placeholders=self.placeholders if placeholders is None else placeholders,
            references=self.references if references is None else references,
            materialization=self.materialization if materialization is None else materialization,
            materialization_name=materialization_name_value,
            column_expressions=self.column_expressions if column_expressions is None else column_expressions
        )

    @classmethod
    def from_sql_model(cls, sql_model: SqlModel, column_expressions: Dict[str, Expression]) -> 'BachSqlModel':
        """ From any SqlModel create a BachSqlModel with the given column definitions. """
        return cls(
            model_spec=sql_model.model_spec,
            placeholders=sql_model.placeholders,
            references=sql_model.references,
            materialization=sql_model.materialization,
            materialization_name=sql_model.materialization_name,
            column_expressions=column_expressions,
        )

    @classmethod
    def _get_placeholders(
        cls,
        dialect: Dialect,
        variables: Dict['DtypeNamePair', Hashable],
        expressions: List[Expression],
    ) -> Dict[str, str]:
        filtered_variables = filter_variables(variables, expressions)
        return get_variable_values_sql(dialect, filtered_variables)


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
    def __init__(
        self,
        model_spec: T,
        placeholders: Mapping[str, Hashable],
        references: Mapping[str, 'SqlModel'],
        materialization: Materialization,
        materialization_name: Optional[str],
        column_expressions: Dict[str, Expression],
        previous: BachSqlModel,
    ) -> None:
        self.previous = previous
        super().__init__(
            model_spec=model_spec,
            placeholders=placeholders,
            references=references,
            materialization=materialization,
            materialization_name=materialization_name,
            column_expressions=column_expressions,
        )

    def copy_override(
        self: 'SampleSqlModel',
        *,
        model_spec: T = None,
        placeholders: Mapping[str, Hashable] = None,
        references: Mapping[str, 'SqlModel'] = None,
        materialization: Materialization = None,
        materialization_name: Union[Optional[str], NotSet] = not_set,
        column_expressions: Dict[str, Expression] = None,
        previous: BachSqlModel = None
    ) -> 'SampleSqlModel':
        """
        Similar to super class's implementation, but adds optional 'previous' parameter
        """
        materialization_name_value = \
            self.materialization_name if materialization_name is not_set else materialization_name
        return self.__class__(
            model_spec=self.model_spec if model_spec is None else model_spec,
            placeholders=self.placeholders if placeholders is None else placeholders,
            references=self.references if references is None else references,
            materialization=self.materialization if materialization is None else materialization,
            materialization_name=materialization_name_value,
            column_expressions=self.column_expressions if column_expressions is None else column_expressions,
            previous=self.previous if previous is None else previous
        )

    @staticmethod
    def get_instance(
        *,
        dialect: Dialect,
        table_name: str,
        previous: BachSqlModel,
        column_expressions: Dict[str, Expression],
        name: str = 'sample_node',
    ) -> 'SampleSqlModel':
        """ Helper function to instantiate a SampleSqlModel """
        sql = 'SELECT * FROM {table_name}'
        return SampleSqlModel(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            placeholders={'table_name': quote_identifier(dialect, table_name)},
            references={},
            materialization=Materialization.CTE,
            materialization_name=None,
            column_expressions=column_expressions,
            previous=previous
        )


class CurrentNodeSqlModel(BachSqlModel):
    @staticmethod
    def get_instance(
        *,
        dialect: Dialect,
        name: str,
        column_names: Tuple[str, ...],
        column_exprs: List[Expression],
        distinct: bool,
        where_clause: Optional[Expression],
        group_by_clause: Optional[Expression],
        having_clause: Optional[Expression],
        order_by_clause: Optional[Expression],
        limit_clause: Expression,
        previous_node: BachSqlModel,
        variables: Dict['DtypeNamePair', Hashable],
    ) -> 'CurrentNodeSqlModel':

        columns_str = ', '.join(expr.to_sql(dialect) for expr in column_exprs)
        distinct_stmt = ' distinct ' if distinct else ''
        where_str = where_clause.to_sql(dialect) if where_clause else ''
        group_by_str = group_by_clause.to_sql(dialect) if group_by_clause else ''
        having_str = having_clause.to_sql(dialect) if having_clause else ''
        order_by_str = order_by_clause.to_sql(dialect) if order_by_clause else ''
        limit_str = limit_clause.to_sql(dialect) if limit_clause else ''

        sql = (
            f"select {distinct_stmt}{columns_str} \n"
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

        return CurrentNodeSqlModel(
            model_spec=CustomSqlModelBuilder(sql=sql, name=name),
            placeholders=BachSqlModel._get_placeholders(dialect, variables, all_expressions),
            references=references,
            materialization=Materialization.CTE,
            materialization_name=None,
            column_expressions={name: expr for name, expr in zip(column_names, column_exprs)},
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


def get_variable_values_sql(
        dialect: Dialect,
        variable_values: Dict['DtypeNamePair', Hashable]
) -> Dict[str, str]:
    """
    Take a dictionary with variable_values and return a dict with the full variable names and the values
    as sql.
    The sql assumes it will be used as values for SqlModels's placeholders. i.e. It will not be format
    escaped, unlike if it would be used directly into SqlModel.sql in which case it would be escaped twice.
    The sql will be proper sql tho, with identifier, strings, etc. properly quoted and escaped.

    :param variable_values: Mapping of variable to value.
    :return: Dictionary mapping full variable name to sql literal
    """
    result = {}
    for dtype_name, value in variable_values.items():
        dtype, name = dtype_name
        value_dtype = value_to_dtype(value)
        if dtype != value_dtype:  # should never happen
            Exception(f'Dtype of value {value}, {value_dtype} does not match registered dtype {dtype}')
        placeholder_name = VariableToken.dtype_name_to_placeholder_name(dtype=dtype, name=name)
        series_type = get_series_type_from_dtype(dtype)
        expr = series_type.value_to_literal(dialect=dialect, value=value, dtype=dtype)
        double_escaped_sql = expr.to_sql(dialect)
        sql = double_escaped_sql.format().format()
        result[placeholder_name] = sql
    return result
