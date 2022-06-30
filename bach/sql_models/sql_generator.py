"""
Copyright 2021 Objectiv B.V.
"""
from typing import List, NamedTuple, Dict, Set, Iterable

from sqlalchemy.engine import Dialect

from sql_models.graph_operations import find_nodes, FoundNode
from sql_models.model import SqlModel, REFERENCE_UNIQUE_FIELD, Materialization
from sql_models.sql_query_parser import raw_sql_to_selects
from sql_models.util import quote_identifier, is_postgres, is_bigquery, DatabaseNotSupportedException


class GeneratedSqlStatement(NamedTuple):
    name: str
    materialization: Materialization
    sql: str


def to_sql(dialect: Dialect, model: SqlModel) -> str:
    """
    Give the sql for the given SqlModel.

    The returned sql can be a single query or statement, or can contain multiple sql statements. The latter
    will be the case if the dependency graph of model contains other models with a materialization that is a
    statement but has non-lasting effect (e.g. creating temporary tables). Then the returned SQL will also
    contain statements for those models.

    If the dependency graph contains models with lasting effect (e.g. create a table or view), then no
    statements for those dependencies are included in the returned sql. The returned sql will assume those
    dependencies have been created already.

    The generated SQL always includes the model itself, regardless of whether it has lasting effect or not.
    Examples: If model.materialization.type_name == 'table' then the final statement of the returned sql will
    create a table. If the materialization is 'query' then the final statement of the returned sql will
    execute a query.

    :param dialect: SQL Dialect
    :param model: model to convert to sql
    :return: executable SQL statement
    """
    # Find all nodes that are a statement (e.g. create a temporary table), but exclude nodes that have a
    # lasting effect (e.g. creating a regular table). Always include the start node
    # Make sure we get the longest possible path to a node (use_last_found_instance=True). That way we can
    # reverse the list and we'll get the nodes that are a dependency for other nodes before the node that
    # depends on them.
    materialized_found_nodes: List[FoundNode] = find_nodes(
        start_node=model,
        function=lambda node: (
            (node is model)
            or
            (node.materialization.is_statement and not node.materialization.has_lasting_effect)
        ),
        first_instance=False
    )

    models = [fn.model for fn in reversed(materialized_found_nodes)]
    statements = _to_sql_list_models(dialect=dialect, models=models)
    sql = ';\n'.join(sql_stat.sql for sql_stat in statements)
    return sql


def to_sql_materialized_nodes(
        dialect: Dialect,
        start_node: SqlModel,
        include_start_node=True,
) -> List[GeneratedSqlStatement]:
    """
    Give list of sql statements:
        * The sql to query the given model
        * The sql to create all views and tables that the given model depends upon
    :param dialect: SQL Dialect
    :param start_node: model to convert to sql
    :return: A list of generated sql statements. Each object contains the name of the model, the
        materialization of the model, and the sql to run the query, or create the table, or create the view.
        The order of the items is significant: earlier statements will create views and/or tables that might
        be used by later statements.
        The names are guaranteed to be unique in the list.
    """
    # find all nodes that are materialized as view or table, and the start_node if needed
    # make sure we get the longest possible path to a node (use_last_found_instance=True). That way we can
    # reverse the list and we'll get the nodes that are a dependency for other nodes before the node that
    # depends on them.

    materialized_found_nodes: List[FoundNode] = find_nodes(
        start_node=start_node,
        function=lambda node: (
            (node is start_node and include_start_node) or node.materialization.is_statement
        ),
        first_instance=False
    )
    models = [fn.model for fn in reversed(materialized_found_nodes)]
    return _to_sql_list_models(dialect=dialect, models=models)


def _to_sql_list_models(dialect: Dialect, models: List[SqlModel]) -> List[GeneratedSqlStatement]:
    """

    """
    result: List[GeneratedSqlStatement] = []
    compiler_cache: Dict[str, List['SemiCompiledTuple']] = {}
    _check_names_unique(models)
    for model in models:
        generated_sql = GeneratedSqlStatement(
            name=model_to_name(model),
            sql=_to_sql_materialized_node(
                dialect=dialect,
                model=model,
                compiler_cache=compiler_cache),
            materialization=model.materialization
        )
        result.append(generated_sql)
    return result


def _to_sql_materialized_node(
        dialect: Dialect,
        model: SqlModel,
        compiler_cache: Dict[str, List['SemiCompiledTuple']],
) -> str:
    """
    Give the sql to query the given model
    :param dialect: SQL Dialect
    :param model: model to convert to sql
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :return: executable select query
    """
    queries = _to_cte_sql(dialect=dialect, compiler_cache=compiler_cache, model=model)
    queries = _filter_duplicate_ctes(queries)
    if len(queries) == 0:
        # _to_cte_sql should never return an empty list, but this make it clear we have a len > 0 below.
        raise Exception('Internal error. No models to compile')

    if len(queries) == 1:
        return _materialize(dialect=dialect, sql_query=queries[0].sql, model=model)

    # case: len(result) > 1
    sql = 'with '
    sql += ',\n'.join(f'{row.quoted_cte_name} as ({row.sql})' for row in queries[:-1])
    sql += '\n' + queries[-1].sql
    return _materialize(dialect=dialect, sql_query=sql, model=model)


def _materialize(dialect: Dialect, sql_query: str, model: SqlModel) -> str:
    """
    Generate sql that wraps the sql_query with the materialization indicated by model.
    :param dialect: SQL Dialect
    :param sql_query: raw sql query
    :param model: model that indicates the materialization and name of the resulting view or table
        (if applicable).
    :return: raw sql
    """

    materialization = model.materialization
    quoted_name = model_to_quoted_name(dialect, model)
    if materialization == Materialization.CTE:
        return sql_query
    if materialization == Materialization.QUERY:
        return sql_query
    if materialization == Materialization.VIEW:
        return f'create view {quoted_name} as {sql_query}'
    if materialization == Materialization.TABLE:
        return f'create table {quoted_name} as {sql_query}'
    if materialization == Materialization.TEMP_TABLE:
        if is_postgres(dialect):
            return f'create temporary table {quoted_name} on commit drop as {sql_query}'
        if is_bigquery(dialect):
            return f'CREATE TEMP TABLE {quoted_name} AS {sql_query}'
        raise DatabaseNotSupportedException(dialect, f'Cannot create temporary table for {dialect.name}')
    if materialization == Materialization.VIRTUAL_NODE:
        return ''
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


def _check_names_unique(models: Iterable[SqlModel]):
    """
    Check that there are no duplicate names in the list of models. Raises an error if duplicates are found.
    """
    seen: Set[str] = set()
    for model in models:
        name = model_to_name(model)
        if name in seen:
            raise ValueError(f'Names of SqlModels need to be unique throughout the graph.'
                             f'Duplicate found: "{name}"')
        seen.add(name)


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


def _to_cte_sql(dialect: Dialect,
                compiler_cache: Dict[str, List[SemiCompiledTuple]],
                model: SqlModel
                ) -> List[SemiCompiledTuple]:
    """
    Recursively build the list of all common table expressions that are needed to generate the sql for
    the given model
    :param dialect: SQL Dialect
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :param model: model to convert to a list of SemiCompiledTuple
    :return:
    """
    if model.hash in compiler_cache:
        return compiler_cache[model.hash]

    # First recursively compile all CTEs that we depend on
    result = []
    reference_names = {
        name: model_to_quoted_name(dialect=dialect, model=reference)
        for name, reference in model.references.items()
    }
    for ref_name, reference in model.references.items():
        if reference.materialization.is_cte:
            result.extend(_to_cte_sql(dialect=dialect, compiler_cache=compiler_cache, model=reference))

    # Compile the actual model
    result.extend(
        _single_model_to_sql(
            dialect=dialect,
            compiler_cache=compiler_cache,
            model=model,
            reference_names=reference_names
        )
    )

    compiler_cache[model.hash] = result
    return result


def model_to_name(model: SqlModel):
    """
    Get the name for the cte/table/view that will be generated from this model, quoted and escaped.
    """
    # max length of an identifier name in Postgres is normally 63 characters. We'll use that as a cutoff
    # here.
    if model.materialization_name is not None:
        return model.materialization_name[0:63]
    name = f'{model.generic_name[0:28]}___{model.hash}'
    return name


def model_to_quoted_name(dialect: Dialect, model: SqlModel):
    """
    Get the name for the cte/table/view that will be generated from this model, quoted and escaped.
    """
    return quote_identifier(dialect, model_to_name(model))


def _single_model_to_sql(dialect: Dialect,
                         compiler_cache: Dict[str, List[SemiCompiledTuple]],
                         model: SqlModel,
                         reference_names: Dict[str, str]
                         ) -> List[SemiCompiledTuple]:
    """
    Split the sql for a given model into a list of separate CTEs.
    :param dialect: SQL Dialect
    :param compiler_cache: Dictionary mapping model hashes to already compiled results
    :param model:
    :param reference_names: mapping of references in the raw sql, to the names of the CTEs that they refer
    :return:
    """
    if model.hash in compiler_cache:
        return compiler_cache[model.hash]
    sql = model.sql
    # If there are any format strings in the placeholder values that need escaping, they should have been
    # escaped by now.
    # Otherwise this will cause trouble the next time we call format() below for the references
    sql = _format_sql(sql=sql, values=model.placeholders_formatted, model=model)
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
        result.append(
            SemiCompiledTuple(quoted_cte_name=quote_identifier(dialect, cte.name), sql=cte.select_sql)
        )
    result.append(
        SemiCompiledTuple(quoted_cte_name=model_to_quoted_name(dialect, model), sql=ctes[-1].select_sql)
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
