import bach
from sql_models.util import is_postgres, is_bigquery, DatabaseNotSupportedException
from abc import abstractmethod


class ListShifterOperation:
    ARRAY_TO_STR_STMT = "'[' || ARRAY_TO_STRING(ARRAY({}), ', ') || ']'"

    FIRST_ELEMENT_SUBLIST_OFFSET = '__first_sublist_offset'
    GENERATED_OFFSET_SUBLIST = '__sublist_item_offset'

    def __init__(self, list_series: bach.SeriesJson, shifting_n: int) -> None:
        self._list_series = list_series
        self._shifting_n = shifting_n

    @abstractmethod
    def r_shift(self) -> bach.SeriesJson:
        """
        Steps for generating shifted sublists:
            1. Cast list_series expression to array (JSON_QUERY_ARRAY)
            2. Generate index of items per sublist
            3. Iterate over generated indexes and extract items from original array
            4. Generate expression for unnesting original array and creating array
                with final sub-lists
        """
        raise NotImplementedError()


class PostgresListShifterOperation(ListShifterOperation):

    def r_shift(self) -> bach.SeriesJson:
        # item indexes are ordinal for PG, therefore we need to subtract 1
        start_gen_series = f'{self.FIRST_ELEMENT_SUBLIST_OFFSET} - 1'
        stop_gen_series = f'{start_gen_series} + {self._shifting_n - 1}'

        # generates a series with the indexes to extract and creates sublist
        # containing items based on generated indexes.
        sub_list_gen_fmt = (
            f"""
            SELECT {{}} -> cast({self.GENERATED_OFFSET_SUBLIST} as int)
            FROM GENERATE_SERIES({start_gen_series}, {stop_gen_series}) 
            as {self.GENERATED_OFFSET_SUBLIST}
            """
        )
        sub_list_gen_expr = bach.expression.Expression.construct(sub_list_gen_fmt, self._list_series)

        # unnest list series and selects the result of the generated sublists
        # validates that index of sublist first element does not exceed shifting length
        unnest_main_list_fmt = (
            f'SELECT {self.ARRAY_TO_STR_STMT} FROM jsonb_array_elements({{}}) '
            f'WITH ORDINALITY rshift(elem, {self.FIRST_ELEMENT_SUBLIST_OFFSET}) '
            f'WHERE {start_gen_series} <= {{}} - {self._shifting_n}'
        )
        agg_sublists_expr = bach.expression.Expression.construct(
            unnest_main_list_fmt,
            sub_list_gen_expr,
            self._list_series,
            self._list_series.json.get_array_length(),
        )

        # format the final agg list from array to string
        return self._list_series.copy_override(
            expression=bach.expression.Expression.construct(
                self.ARRAY_TO_STR_STMT,
                agg_sublists_expr,
            )
        )
    
    def count_sublist_occurrence(self, shift_type='right') -> bach.SeriesInt64:
        if shift_type != 'right':
            raise Exception(f'{shift_type} is not implemented. "right" shift is supported only.')
        
        shifted_list = self.r_shift()
        shifted_list = shifted_list.materialize(node_name='shifted_list')
        
        unnested_sublist_series = shifted_list.copy_override(
            expression=bach.expression.Expression.construct(
                'unnest(array(select sublist :: text from jsonb_array_elements({}::jsonb) as sublist))',
                shifted_list
            ),
        )
        df = unnested_sublist_series.to_frame()
        df['count'] = 1
        return df.groupby(self._list_series.name)['count'].count()


class BigQueryListShifterOperation(ListShifterOperation):

    def r_shift(self) -> bach.SeriesJson:
        start_gen_series = f'{self.FIRST_ELEMENT_SUBLIST_OFFSET}'
        stop_gen_series = f'{start_gen_series} + {self._shifting_n - 1}'

        # generates a series with the indexes to extract and creates sublist
        # containing items based on generated indexes.
        sub_list_gen_fmt = (
            f"""
            SELECT JSON_QUERY_ARRAY({{}})[OFFSET({self.GENERATED_OFFSET_SUBLIST})]
            FROM UNNEST(GENERATE_ARRAY({start_gen_series}, {stop_gen_series})) 
            as {self.GENERATED_OFFSET_SUBLIST}
            """
        )
        sub_list_gen_expr = bach.expression.Expression.construct(sub_list_gen_fmt, self._list_series)

        # unnest list series and selects the result of the generated sublists
        # validates that index of sublist first element does not exceed shifting length
        unnest_main_list_fmt = (
            f'SELECT {self.ARRAY_TO_STR_STMT} FROM UNNEST(JSON_QUERY_ARRAY({{}})) '
            f'WITH OFFSET AS {self.FIRST_ELEMENT_SUBLIST_OFFSET} '
            f'WHERE {start_gen_series} <= {{}} - {self._shifting_n}'
        )
        agg_sublists_expr = bach.expression.Expression.construct(
            unnest_main_list_fmt,
            sub_list_gen_expr,
            self._list_series,
            self._list_series.json.get_array_length(),
        )

        # format the final agg list from array to string
        return self._list_series.copy_override(
            expression=bach.expression.Expression.construct(
                self.ARRAY_TO_STR_STMT,
                agg_sublists_expr,
            )
        )
    
    def count_sublist_occurrence(self, shift_type='right') -> bach.SeriesInt64:
        if shift_type != 'right':
            raise Exception(f'{shift_type} is not implemented. "right" shift is supported only.')
        
        shifted_list = self.r_shift()
        # convert to array, this way we can just convert array items as rows
        # by doing FROM {base_node}, {base_node.shifted_list}
        shifted_list = shifted_list.copy_override(
            expression=bach.expression.Expression.construct('JSON_QUERY_ARRAY({})', shifted_list)
        )
        shifted_list = shifted_list.materialize(node_name='shifted_list')

        from sql_models.model import CustomSqlModelBuilder
        from sql_models.util import quote_identifier

        sublist_identifier = quote_identifier(shifted_list.engine.dialect, name='sublist')
        shifted_list_identifier = quote_identifier(shifted_list.engine.dialect, name=shifted_list.name)
        column_stmt = (
            f"{sublist_identifier} as {shifted_list_identifier}, "
            f"count(1) as {quote_identifier(shifted_list.engine.dialect, 'count')}"
        )

        from sql_models.model import CustomSqlModelBuilder
        sql = (
            f"SELECT {column_stmt} FROM "
            f"{{{{current_node}}}}, {{{{current_node}}}}.{shifted_list_identifier} AS {sublist_identifier} "
            f" GROUP BY {sublist_identifier}"
        )
        model_builder = CustomSqlModelBuilder(sql=sql, name='sublist_counter')
        sql_model = model_builder(current_node=shifted_list.base_node)

        df = bach.DataFrame.from_model(
            engine=shifted_list.engine,
            model=sql_model,
            index=[shifted_list.name],
            all_dtypes={shifted_list.name: bach.SeriesJson.dtype, 'count': bach.SeriesInt64.dtype}
        )
        return df['count']


def bach_func_gram(list_series: bach.SeriesJson, n: int) -> bach.SeriesJson:
    engine = list_series.engine
    if is_postgres(engine):
        return PostgresListShifterOperation(list_series=list_series, shifting_n=n).r_shift()
    
    if is_bigquery(engine):
        return BigQueryListShifterOperation(list_series=list_series, shifting_n=n).r_shift()
    
    raise DatabaseNotSupportedException(engine)

    
# import os
# from sqlalchemy import create_engine
# pg_engine = create_engine("postgresql://objectiv:@localhost:5432/objectiv")
# bq_engine = create_engine(
#     "bigquery://objectiv-production/snowplow",
#     credentials_path=f"{os.getcwd().replace('notebooks', 'modelhub')}/.secrets/objectiv-production--bigquery-read-only.json",
# )
