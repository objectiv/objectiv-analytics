"""
Copyright 2022 Objectiv B.V.
"""
from bach.dataframe import DataFrameOrSeries


def display_sql_as_markdown(obj: DataFrameOrSeries) -> None:
    """
    Displays in the frontend (notebook) the result from :py:meth:`DataFrame.view_sql`
    into Markdown-friendly format.

    :param obj: DataFrame or Series from where to obtain the generated sql.

    .. note::
        Requires the IPython package, if not installed the query will be print instead
    """
    sql_str = obj.view_sql()
    try:
        from IPython.display import display, Markdown
        display(Markdown(f'```sql\n{sql_str}```'))
    except ModuleNotFoundError:
        print(sql_str)
