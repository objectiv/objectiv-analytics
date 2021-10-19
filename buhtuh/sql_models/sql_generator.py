"""
Copyright 2021 Objectiv B.V.
"""
from typing import List, NamedTuple, Dict

from sql_models.model import SqlModel, REFERENCE_UNIQUE_FIELD
from sql_models.sql_query_parser import raw_sql_to_selects


def to_sql(model: SqlModel) -> str:
    """
    Give the sql to query the given model
    :param model: model to convert to sql
    :return: executable select query
    """
    compiler_cache: Dict[str, List[SemiCompiledTuple]] = {}
    queries = _to_cte_sql(compiler_cache=compiler_cache, model=model)
    queries = _filter_duplicate_ctes(queries)
    if len(queries) == 0:
        # _to_cte_sql should never return an empty list, but this make it clear we have a len > 0 below.
        raise Exception('Internal error. No models to compile')

    if len(queries) == 1:
        return queries[0].sql

    # case: len(result) > 1
    sql = 'with '
    sql += ',\n'.join(f'{row.cte_name} as ({row.sql})' for row in queries[:-1])
    sql += '\n' + queries[-1].sql
    return sql


class SemiCompiledTuple(NamedTuple):
    """
    Object representing a single CTE select statement from a big select statement
    with common table expressions.
    """
    # This is very similar to the CteTuple in sql_query_parser. However here cte_name is mandatory.
    cte_name: str
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
        if query.cte_name not in seen:
            seen[query.cte_name] = query.sql
            result.append(query)
        elif seen[query.cte_name] != query.sql:
            raise Exception(f'Encountered the CTE {query.cte_name} multiple times, but with different '
                            f'definitions. HINT: use "{{REFERENCE_UNIQUE_FIELD}}" in the sql definition '
                            f'to make CTE names unique between different instances of the same model.\n'
                            f'first: {seen[query.cte_name]}\n'
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

    if not model.references:
        return _single_model_to_sql(compiler_cache=compiler_cache, model=model, reference_names={})
    result = []
    reference_names = {name: model_to_cte_name(reference) for name, reference in model.references.items()}
    for ref_name, reference in model.references.items():
        result.extend(_to_cte_sql(compiler_cache=compiler_cache, model=reference))
    result.extend(
        _single_model_to_sql(compiler_cache=compiler_cache, model=model, reference_names=reference_names))

    compiler_cache[model.hash] = result
    return result


def model_to_cte_name(model):
    # max length of an identifier name in Postgres is normally 63 characters. We'll use that as a cutoff
    # here.
    # TODO: two compilation phases:
    #  1) get all cte names
    #  2) generate actual sql. Only for CTEs with conflicting names add the hash
    return f'{model.generic_name[0:28]}___{model.hash}'


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
    # Make sure that if there are any format strings in the properties that they get escaped. Otherwise this
    # would cause trouble the next time we call format() below for the references
    escaped_properties = {key: _escape_value(value) for key, value in model.properties_formatted.items()}
    sql = _format_sql(sql=sql, values=escaped_properties, model=model)
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
        result.append(SemiCompiledTuple(cte_name=cte.name, sql=cte.select_sql))
    result.append(SemiCompiledTuple(cte_name=model_to_cte_name(model), sql=ctes[-1].select_sql))

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


def _escape_value(value: str) -> str:
    """ Escape value for python's format() function. i.e. `_escape_value(value).format() == value` """
    return value.replace('{', '{{').replace('}', '}}')
