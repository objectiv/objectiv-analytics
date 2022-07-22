"""
Copyright 2021 Objectiv B.V.
"""
import json
import os

from typing import List, Generic, TypeVar
# added for metabase export
import requests

from bach import DataFrame, Series, SeriesString, SeriesJson
from bach.expression import Expression, quote_string, quote_identifier, join_expressions
from bach.series.series_json import JsonAccessor
from bach.types import register_dtype
from sql_models.util import is_postgres, DatabaseNotSupportedException, is_bigquery


TSeriesJson = TypeVar('TSeriesJson', bound='SeriesJson')


class ObjectivStack(JsonAccessor, Generic[TSeriesJson]):
    """
    Specialized JsonAccessor that has functions to work on SeriesJsons whose data consists of an array
    of objects.
    """

    def get_from_context_with_type_series(self, type: str, key: str, dtype='string'):
        """
        .. _get_from_context_with_type_series:

        Returns the value of `key` from the first context in an Objectiv stack where `_type` matches `type`.

        :param type: the _type to search for in the contexts of the stack.
        :param key: the value of the key to return of the context with matching type.
        :param dtype: the dtype of the series to return.
        :returns: a series of type `dtype`
        """
        dialect = self._series_object.engine.dialect
        if is_postgres(dialect):
            return self._postgres_get_from_context_with_type_series(type, key, dtype)
        if is_bigquery(dialect):
            return self._bigquery_get_from_context_with_type_series(type, key, dtype)
        raise DatabaseNotSupportedException(dialect)

    def _postgres_get_from_context_with_type_series(self, type: str, key: str, dtype='string'):
        dialect = self._series_object.engine.dialect
        expression_str = f'''
        jsonb_path_query_first({{}},
        \'$[*] ? (@._type == $type)\',
        \'{{"type":{quote_identifier(dialect, type)}}}\') ->> {{}}'''
        expression = Expression.construct(
            expression_str,
            self._series_object,
            Expression.string_value(key)
        )
        return self._series_object.copy_override_dtype(dtype).copy_override(expression=expression)

    def _bigquery_get_from_context_with_type_series(self, type: str, key: str, dtype='string'):
        select_ctx_expression = Expression.construct(
            '''(
              select first_value(ctx) over (order by pos)
              from unnest(json_query_array({}, '$')) as ctx with offset as pos
              where json_value(ctx, '$."_type"') = {}
            )''',
            self._series_object,
            Expression.string_value(type)
        )
        ctx_series = self._series_object.copy_override(expression=select_ctx_expression)
        as_str = dtype == 'string'
        value_series = ctx_series.json.get_value(key=key, as_str=as_str)
        return value_series.copy_override_dtype(dtype)


@register_dtype(value_types=[], override_registered_types=True)
class SeriesGlobalContexts(SeriesJson):
    """
    Objectiv Global Contexts series. This series type contains functionality specific to the Objectiv Global
    Contexts.
    """
    dtype = 'objectiv_global_context'

    class GlobalContexts(ObjectivStack):
        @property
        def cookie_id(self):
            """
            .. _gc_cookie_id:

            Returns cookie id from the global contexts.
            """
            return self.get_from_context_with_type_series("CookieIdContext", "cookie_id")

        @property
        def user_agent(self):
            """
            .. _gc_user_agent:

            Returns user agent string from the global contexts.
            """
            return self.get_from_context_with_type_series("HttpContext", "user_agent")

        @property
        def application(self):
            """
            .. _gc_application:

            Returns application id from the global contexts.
            """
            return self.get_from_context_with_type_series("ApplicationContext", "id")

    @property
    def objectiv(self):
        """
        Accessor for Objectiv stack data. All methods of :py:attr:`json` can also be accessed with this
        accessor. Same as :py:attr:`obj`

        .. autoclass:: modelhub.series.ObjectivStack
            :members:
            :noindex:

        """
        return ObjectivStack(self)

    @property
    def obj(self):
        """
        Accessor for Objectiv stack data. All methods of :py:attr:`json` can also be accessed with this
        accessor. Same as :py:attr:`objectiv`

        .. autoclass:: modelhub.series.ObjectivStack
            :members:
            :noindex:

        """
        return ObjectivStack(self)

    @property
    def global_contexts(self):
        """
        Accessor for Objectiv global context data. All methods of :py:attr:`json` and :py:attr:`objectiv` can
        also be accessed with this accessor. Same as :py:attr:`gc`

        .. autoclass:: modelhub.series.SeriesGlobalContexts.GlobalContexts
            :members:

        """
        return self.GlobalContexts(self)

    @property
    def gc(self):
        """
        Accessor for Objectiv global context data. All methods of :py:attr:`json` and :py:attr:`objectiv` can
        also be accessed with this accessor. Same as :py:attr:`global_contexts`

        .. autoclass:: modelhub.series.SeriesGlobalContexts.GlobalContexts
            :members:
            :noindex:

        """
        return self.GlobalContexts(self)


@register_dtype([], override_registered_types=True)
class SeriesLocationStack(SeriesJson):
    """
    Objectiv Location Stack series. This series type contains functionality specific to the Objectiv Location
    Stack.
    """
    dtype = 'objectiv_location_stack'

    class LocationStack(ObjectivStack):
        @property
        def navigation_features(self):
            """
            .. _ls_navigation_features:

            Returns the navigation stack from the location stack.
            """
            # type ignore, as mypy doesn't like a dict in a Slice
            return self[{'_type': 'NavigationContext'}: None]  # type: ignore

        @property
        def feature_stack(self) -> 'SeriesLocationStack':
            """
            .. _ls_feature_stack:

            Returns the feature stack from the location stack. The context objects only contain the `_type`
            and a `id` key.
            """
            keys = ['_type', 'id']
            engine = self._series_object.engine
            if is_postgres(engine):
                return self._postgres_filter_keys_of_dicts(keys)
            if is_bigquery(engine):
                return self._bigquery_filter_keys_of_dicts(keys)
            raise DatabaseNotSupportedException(engine)

        def _postgres_filter_keys_of_dicts(self, keys: List[str]) -> 'TSeriesJson':
            """
            Return a new Series, that consists of the same top level array, but with all the sub-dictionaries
            having only their original fields if that field is listed in the keys parameter.

            Postgres only.
            """
            jsonb_build_object_str = [f"{quote_string(self._series_object.engine, key)}" for key in keys]
            expression_str = f'''(
                select jsonb_agg((
                    select json_object_agg(items.key, items.value)
                    from jsonb_each(objects.value) as items
                    where items.key in ({", ".join(jsonb_build_object_str)})))
                from jsonb_array_elements({{}}) as objects)
            '''
            expression = Expression.construct(
                expression_str,
                self._series_object
            )
            return self._series_object.copy_override(expression=expression)

        def _bigquery_filter_keys_of_dicts(self, keys: List[str]) -> 'TSeriesJson':
            """
            Return a new Series, that consists of the same top level array, but with all the sub-dictionaries
            having only the fields that are listed in the keys parameter. If the field didn't previously
            exist then it will have the value NULL.

            The fields of the sub-dictionaries MUST be scalar values (i.e. string, number, or boolean).
            Bigquery only.
            """
            # We unnest the json-array, and then for every json object in the array we build a copy of that
            # json object, but with only the keys that are listed in the `keys` variable.
            object_entries_expressions = []
            for i, key in enumerate(keys):
                if '"' in key:
                    raise ValueError(f'key values containing double quotes are not supported. key: {key}')
                # Using JSON_VALUE here means this only works with scalar, but we warn the user in the
                # docstring of this.
                entry_expr = Expression.construct(
                    '''JSON_VALUE(item, '$."{}"') as {}''',
                    Expression.raw(key),
                    Expression.identifier(key)
                )
                object_entries_expressions.append(entry_expr)
            expression = Expression.construct(
                '''TO_JSON_STRING(ARRAY(
                    SELECT STRUCT({})
                    FROM UNNEST (JSON_QUERY_ARRAY({}, '$')) AS item WITH OFFSET AS pos
                    ORDER BY pos))''',
                join_expressions(object_entries_expressions),
                self._series_object
            )
            return self._series_object.copy_override(expression=expression)

        @property
        def nice_name(self) -> 'SeriesString':
            """
            .. _ls_nice_name:

            Returns a nice name for the location stack. This is a human readable name for the data in the
            feature stack.
            """
            engine = self._series_object.engine
            if is_postgres(engine):
                expression = self._postgres_nice_name()
            elif is_bigquery(engine):
                expression = self._bigquery_nice_name()
            else:
                raise DatabaseNotSupportedException(engine)
            return self._series_object.copy_override_type(SeriesString).copy_override(expression=expression)

        def _bigquery_nice_name(self) -> Expression:
            # last_element_nice_expr turns something with _type='SectionContext' and id='section_id'
            # into something like 'Section: section_id'
            last_element = self._series_object.json[-1]
            last_element_nice_expr = Expression.construct(
                """
                    REGEXP_REPLACE(
                        REGEXP_REPLACE({}, '([a-z])([A-Z])', r'\\1 \\2'),
                        ' Context$',
                        ''
                    ) || ': ' || {}
                """,
                last_element.json.get_value('_type', as_str=True),
                last_element.json.get_value('id', as_str=True)
            )

            # For all other elements in the stack we do something similar as we did with the last element
            # in last_element_nice_expr. But we prepend 'Located at', and couple the elements with ' => '.
            # Example output value for other_elements_expr:
            #   'located at Web Document: #document => Section: x => Section: y'

            # element_json allows us to reuse code from the accessor without duplicating. 'element' will be
            # set by iterating over the json array in the query below.
            element_json = self._series_object.copy_override(expression=Expression.construct('element'))
            other_elements_expr = Expression.construct(
                """
                    CASE WHEN {} > 1
                    THEN ' located at ' || (SELECT STRING_AGG(
                                    REGEXP_REPLACE(
                                        REGEXP_REPLACE({}, '([a-z])([A-Z])', r'\\1 \\2'),
                                        ' Context$',
                                        ''
                                    ) || ': ' || {},
                                    ' => '
                                )
                                FROM UNNEST (JSON_QUERY_ARRAY({}, '$')) AS element WITH OFFSET AS pos
                                WHERE pos < ({} - 1)
                            )
                    ELSE ''
                    END
                """,
                self._series_object.json.get_array_length(),
                element_json.json.get_value('_type', as_str=True),
                element_json.json.get_value('id', as_str=True),
                self._series_object,
                self._series_object.json.get_array_length(),
            )
            return Expression.construct('({}) || ({})', last_element_nice_expr, other_elements_expr)

        def _postgres_nice_name(self) -> Expression:
            expression = Expression.construct(
                f"""(
                    select string_agg(
                            replace(
                                regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                                ' Context',
                                ''
                            ) || ': ' || (value ->> 'id'),
                            ' => ')
                    from jsonb_array_elements({{}}) with ordinality
                    where ordinality = jsonb_array_length({{}})
                ) || (
                    case when jsonb_array_length({{}}) > 1
                         then ' located at ' || (select string_agg(
                                replace(
                                    regexp_replace(value ->> '_type', '([a-z])([A-Z])', '\\1 \\2', 'g'),
                                    ' Context',
                                    ''
                                ) || ': ' || (value ->> 'id'),
                                ' => ')
                            from jsonb_array_elements({{}}) with ordinality
                            where ordinality < jsonb_array_length({{}})
                        )
                        else '' end
                )""",
                self._series_object,
                self._series_object,
                self._series_object,
                self._series_object,
                self._series_object
            )
            return expression

    @property
    def objectiv(self):
        """
        Accessor for Objectiv stack data. All methods of :py:attr:`json` can also be accessed with this
        accessor. Same as :py:attr:`obj`

        .. autoclass:: modelhub.series.ObjectivStack
            :members:
            :noindex:

        """
        return ObjectivStack(self)

    @property
    def obj(self):
        """
        Accessor for Objectiv stack data. All methods of :py:attr:`json` can also be accessed with this
        accessor. Same as :py:attr:`objectiv`

        .. autoclass:: modelhub.series.ObjectivStack
            :members:
            :noindex:

        """
        return ObjectivStack(self)

    @property
    def location_stack(self):
        """
        Accessor for Objectiv location stack data. All methods of :py:attr:`json` and :py:attr:`objectiv`
        can also be accessed with this accessor. Same as :py:attr:`ls`

        .. autoclass:: modelhub.series.SeriesLocationStack.LocationStack
            :members:

        """
        return self.LocationStack(self)

    @property
    def ls(self):
        """
        Accessor for Objectiv location stack data. All methods of :py:attr:`json` and :py:attr:`objectiv` can
        also be accessed with this accessor. Same as :py:attr:`location_stack`

        .. autoclass:: modelhub.series.SeriesLocationStack.LocationStack
            :members:
            :noindex:

        """
        return self.LocationStack(self)


class MetaBaseException(Exception):
    pass


class MetaBase:

    _session_id = None

    # config per model
    config = {
        'default': {
            'display': 'bar',
            'name': 'Generic / default graph',
            'description': 'This is a generic graph',
            'result_metadata': [],
            'dimensions': [],
            'metrics': []
        },
        'unique_users': {
            'display': 'line',
            'name': 'Unique Users',
            'description': 'Unique Users',
            'result_metadata': [],
            'dimensions': ['date'],
            'metrics': ['count']
        },
        'unique_sessions': {
            'display': 'bar',
            'name': 'Unique Sessions',
            'description': 'Unique sessions from Model Hub',
            'result_metadata': [],
            'dimensions': ['date'],
            'metrics': ['count']
        }
    }

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 url: str = None,
                 database_id: int = None,
                 dashboard_id: int = None,
                 collection_id: int = None,
                 web_url: str = None):
        if username:
            self._username = username
        else:
            self._username = os.getenv('METABASE_USERNAME', 'objectiv')

        if password:
            self._password = password
        else:
            self._password = os.getenv('METABASE_PASSWORD', '')

        if database_id:
            self._database_id = database_id
        else:
            self._database_id = int(os.getenv('METABASE_DATABASE_ID', 1))

        if dashboard_id:
            self._dashboard_id = dashboard_id
        else:
            self._dashboard_id = int(os.getenv('METABASE_DASHBOARD_ID', 1))

        if collection_id:
            self._collection_id = collection_id
        else:
            self._collection_id = int(os.getenv('METABASE_COLLECTION_ID', 0))

        if url:
            self._url = url
        else:
            self._url = os.getenv('METABASE_URL', '2')

        if web_url:
            self._web_url = web_url
        else:
            self._web_url = os.getenv('METABASE_WEB_URL', self._url)

        # config by calling dataframe / model
        self._df = None
        self._config = None

    def _get_new_session_id(self) -> str:
        data = json.dumps({'username': self._username, 'password': self._password})
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f'{self._url}/api/session', data=data, headers=headers)

        if response.status_code != 200:
            raise MetaBaseException(f'Session ID request failed with code: {response.status_code}')

        response_json = response.json()

        if 'id' in response_json:
            return response_json['id']
        else:
            raise KeyError('Could not find id in JSON response from MetaBase')

    def _get_session_id(self):
        if MetaBase._session_id is None:
            MetaBase._session_id = self._get_new_session_id()

        return MetaBase._session_id

    def _do_request(self, url: str, data: dict = None, method='post') -> requests.Response:
        if data is None:
            data = {}
        headers = {
            'Content-Type': 'application/json',
            'X-Metabase-Session': self._get_session_id()
        }
        if method == 'get':
            response = requests.get(url, data=json.dumps(data), headers=headers)
        elif method == 'post':
            response = requests.post(url, data=json.dumps(data), headers=headers)
        elif method == 'put':
            response = requests.put(url, data=json.dumps(data), headers=headers)
        else:
            raise MetaBaseException(f'Unsupported method called: {method}')

        return response

    def add_update_card(self, df: DataFrame, config: dict) -> dict:
        data = {
            'collection_id': self._collection_id,
            'dataset_query': {
                'database': self._database_id,
                'native': {
                    'query': df.view_sql()
                },
                'type': 'native'
            },
            'description': config['description'],
            'display': config['display'],
            'name': config['name'],
            'result_metadata': config['result_metadata'],
            'visualization_settings': {
                'graph.dimensions': config['dimensions'],
                'graph.metrics': config['metrics']
            }
        }
        response = self._do_request(url=f'{self._url}/api/card', method='get')

        if response.status_code != 200:
            raise MetaBaseException(f'Failed to obtain list of existing cards with code: '
                                    f'{response.status_code}')

        # the default is to create a new card
        method = 'post'
        url = f'{self._url}/api/card'

        # but if we can find an existing card that matches
        # we update, rather than create
        for card in response.json():
            if card['description'] == config['description'] and \
                    card['name'] == config['name']:

                card_id = card['id']
                url = f'{self._url}/api/card/{card_id}'
                method = 'put'

        response = self._do_request(url=url, data=data, method=method)
        if response.status_code != 202:
            raise MetaBaseException(f'Failed to add card @ {url} with {data} (code={response.status_code})')

        response_json = response.json()
        if 'id' in response_json:
            card_id = response_json['id']
        else:
            raise MetaBaseException(f'No card ID in response {response_json}')

        dashboard_info = self.update_dashboard(card_id=card_id, dashboard_id=self._dashboard_id)

        return {
            'card': f'{self._web_url}/card/{card_id}',
            'dashboard': f'{self._web_url}/dashboard/{self._dashboard_id}-'
                         f'{dashboard_info["name"].lower().replace(" ", "-")}',
            'username': self._username,
            'password': self._password
        }

    def update_dashboard(self, card_id: int, dashboard_id: int):
        response = self._do_request(f'{self._url}/api/dashboard/{dashboard_id}', method='get')

        if response.status_code != 200:
            raise MetaBaseException(f'Failed to get cards list for dashboard {dashboard_id} '
                                    f'(code={response.status_code}')

        dashboard_info = response.json()
        # list of card_id's currently on the dashboard
        cards = [card['card']['id'] for card in dashboard_info['ordered_cards']]
        if card_id not in cards:

            url = f'{self._url}/api/dashboard/{dashboard_id}/cards'
            data = {'cardId': card_id}

            response = self._do_request(url=url, method='post', data=data)

            if response.status_code != 200:
                raise ValueError(f'Adding card to dashboard failed with code: {response.status_code}')
        return dashboard_info

    def to_metabase(self, df: DataFrame, model_type: str = None, config: dict = None):
        if isinstance(df, Series):
            df = df.to_frame()
        if not config:
            config = {}

        if model_type in MetaBase.config:
            card_config = MetaBase.config[model_type]
        else:
            card_config = MetaBase.config['default']

        card_config['dimensions'] = [k for k in df.index.keys()]
        card_config['metrics'] = [k for k in df.data.keys()]

        card_config.update(config)
        return self.add_update_card(df, card_config)
