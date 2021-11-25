"""
Copyright 2021 Objectiv B.V.
"""
from typing import List, NamedTuple, Dict

from sql_models.graph_operations import find_nodes, FoundNode
from sql_models.model import SqlModel, REFERENCE_UNIQUE_FIELD, Materialization
from sql_models.sql_query_parser import raw_sql_to_selects
from sql_models.util import quote_identifier


def to_sql(model: SqlModel) -> str:
    """
    Give the sql to query the given model
    :param model: model to convert to sql
    :return: executable select query
    """
    compiler_cache: Dict[str, List['SemiCompiledTuple']] = {}
    return _to_sql_materialized_node(model=model, compiler_cache=compiler_cache)


def to_sql_materialized_nodes(start_node: SqlModel, include_start_node=True) -> List[str]:
    """
    Give list of sql statements:
        * The sql to query the given model
        * The sql to create all views and tables that the given model depends upon
    :param start_node: model to convert to sql
    :return: A list of sql statements. The final statement will be the query for the given start_node.
        Earlier statements will be create statements for views and/or tables.
    """
    result = []
    compiler_cache: Dict[str, List['SemiCompiledTuple']] = {}
    # find all nodes that are materialized as view or table, and the start_node if needed
    # make sure we get the longest possible path to a node (use_last_found_instance=True). That way we can
    # reverse the list and we'll get the nodes that are a dependency for other nodes before the node that
    # depends on them.

    def select_nodes(node: SqlModel) -> bool:
        return (node is start_node and include_start_node) \
               or node.materialization in (
                Materialization.VIEW, Materialization.TABLE, Materialization.TEMP_TABLE_DROP_ON_COMMIT
               )

    materialized_found_nodes: List[FoundNode] = find_nodes(
        start_node=start_node,
        function=select_nodes,
        use_last_found_instance=True
    )
    for found_node in reversed(materialized_found_nodes):
        result.append(_to_sql_materialized_node(model=found_node.model, compiler_cache=compiler_cache))
    return result


def _to_sql_materialized_node(
        model: SqlModel,
        compiler_cache: Dict[str, List['SemiCompiledTuple']]
) -> str:
    """
    Give the sql to query the given model
    :param model: model to convert to sql
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :return: executable select query
    """
    queries = _to_cte_sql(compiler_cache=compiler_cache, model=model)
    queries = _filter_duplicate_ctes(queries)
    if len(queries) == 0:
        # _to_cte_sql should never return an empty list, but this make it clear we have a len > 0 below.
        raise Exception('Internal error. No models to compile')

    if len(queries) == 1:
        return _materialize(queries[0].sql, model)

    # case: len(result) > 1
    sql = 'with '
    sql += ',\n'.join(f'{row.quoted_cte_name} as ({row.sql})' for row in queries[:-1])
    sql += '\n' + queries[-1].sql
    return _materialize(sql, model)


def _materialize(sql_query: str, model: SqlModel) -> str:
    """
    Generate sql that wraps the sql_query with the materialization indicated by model.
    :param sql_query: raw sql query
    :param model: model that indicates the materialization and name of the resulting view or table
        (if applicable).
    :return: raw sql
    """

    materialization = model.materialization
    quoted_name = model_to_quoted_name(model)
    if materialization == Materialization.CTE:
        return sql_query
    if materialization == Materialization.VIEW:
        return f'create view {quoted_name} as {sql_query}'
    if materialization == Materialization.TABLE:
        return f'create table {quoted_name} as {sql_query}'
    if materialization == Materialization.TEMP_TABLE_DROP_ON_COMMIT:
        return f'create temporary table {quoted_name} on commit drop as {sql_query}'
    raise Exception(f'Unsupported Materialization value: {materialization}')


class SemiCompiledTuple(NamedTuple):
    """
    Object representing a single CTE select statement from a big select statement
    with common table expressions.
    """
    # This is very similar to the CteTuple in sql_query_parser. However here cte_name is mandatory and
    # quoted and escaped.
    quoted_cte_name: str
    sql: str


def _filter_duplicate_ctes(queries: List[SemiCompiledTuple]) -> List[SemiCompiledTuple]:
    """
    Filter duplicate CTEs from the list
    If a cte occurs multiple times, then only keep the first occurrence.
    Throw an error if not all of the occurrences are the same.
    :param queries:
    :return:
    """
    seen: Dict[str, str] = {}
    result = []
    for query in queries:
        if query.quoted_cte_name not in seen:
            seen[query.quoted_cte_name] = query.sql
            result.append(query)
        elif seen[query.quoted_cte_name] != query.sql:
            raise Exception(f'Encountered the CTE {query.quoted_cte_name} multiple times, but with different '
                            f'definitions. HINT: use "{{REFERENCE_UNIQUE_FIELD}}" in the sql definition '
                            f'to make CTE names unique between different instances of the same model.\n'
                            f'first: {seen[query.quoted_cte_name]}\n'
                            f'second: {query.sql}\n')
    return result


def _to_cte_sql(compiler_cache: Dict[str, List[SemiCompiledTuple]],
                model: SqlModel) -> List[SemiCompiledTuple]:
    """
    Recursively build the list of all common table expressions that are needed to generate the sql for
    the given model
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :param model: model to convert to a list of SemiCompiledTuple
    :return:
    """
    if model.hash in compiler_cache:
        return compiler_cache[model.hash]

    # First recursively compile all CTEs that we depend on
    result = []
    reference_names = {
        name: model_to_quoted_name(reference) for name, reference in model.references.items()
    }
    for ref_name, reference in model.references.items():
        if reference.materialization == Materialization.CTE:
            result.extend(_to_cte_sql(compiler_cache=compiler_cache, model=reference))

    # Compile the actual model
    result.extend(
        _single_model_to_sql(compiler_cache=compiler_cache, model=model, reference_names=reference_names)
    )

    compiler_cache[model.hash] = result
    return result


def model_to_quoted_name(model: SqlModel):
    """
    Get the name for the cte/table/view that will be generated from this model, quoted and escaped.
    """
    # max length of an identifier name in Postgres is normally 63 characters. We'll use that as a cutoff
    # here.
    # TODO: two compilation phases:
    #  1) get all cte/view/table names
    #  2) generate actual sql. Only for CTEs with conflicting names add the hash
    name = f'{model.generic_name[0:28]}___{model.hash}'
    return quote_identifier(name)


def _single_model_to_sql(compiler_cache: Dict[str, List[SemiCompiledTuple]],
                         model: SqlModel,
                         reference_names: Dict[str, str]) -> List[SemiCompiledTuple]:
    """
    Split the sql for a given model into a list of separate CTEs.
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :param model:
    :param reference_names: mapping of references in the raw sql, to the names of the CTEs that they refer
    :return:
    """
    if model.hash in compiler_cache:
        return compiler_cache[model.hash]
    sql = model.sql
    # If there are any format strings in the properties that need escaping, they should have been by now.
    # Otherwise this would cause trouble the next time we call format() below for the references
    sql = _format_sql(sql=sql, values=model.properties_formatted, model=model)
    # {{id}} (==REFERENCE_UNIQUE_FIELD) is a special placeholder that gets the unique model identifier,
    # which can be used in templates to make sure that if a model gets used multiple times,
    # the cte-names are still unique.
    _reference_names = dict(**reference_names)
    _reference_names[REFERENCE_UNIQUE_FIELD] = model.hash
    sql = _format_sql(sql=sql, values=_reference_names, model=model)
    ctes = raw_sql_to_selects(sql)
    result: List[SemiCompiledTuple] = []
    for cte in ctes[:-1]:
        # For all CTEs the name should be set. Only for the final select (== cte[-1]) it will be None.
        assert cte.name is not None
        result.append(SemiCompiledTuple(quoted_cte_name=quote_identifier(cte.name), sql=cte.select_sql))
    result.append(
        SemiCompiledTuple(quoted_cte_name=model_to_quoted_name(model), sql=ctes[-1].select_sql)
    )

    compiler_cache[model.hash] = result
    return result


def _format_sql(sql: str, values: Dict[str, str], model: SqlModel):
    """ Execute sql.format(**values), and if that fails raise a clear exception. """
    try:
        sql = sql.format(**values)
    except Exception as exc:
        raise Exception(f'Failed to format sql for model {model.generic_name}. \n'
                        f'Format values: {values}. \n'
                        f'Sql: {sql}') from exc
    return sql
