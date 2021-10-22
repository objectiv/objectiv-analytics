import pickle
import base64
import json
from js import XMLHttpRequest
from typing import List, Dict, Any

"""
simple http/json based wrapper to remotely run pg queries

TODO:
- fix sessions /cookies for transactions
- probably lots of other stuff

DONE:
- *__make synchronous__*
- send close connection on close of connection (__exit__ / close())
- proper typing (serialization is JSON for now (UUID / Timestamps / JSON))

"""


class Result:

    def __init__(self, rows: List):
        self.rows: List = rows

    def fetchall(self) -> List[List]:
        result: List = []
        for row in self.rows:
            result.append([row[c] for c in row])

        return result

    def fetchall_dict(self) -> List[Dict[str, Any]]:
        self.rows


class Cursor:
    def __init__(self, connection: 'Connection'):
        self._connection = connection
        self._result = None

    def execute(self, query: str, **kwargs):
        self._result = self._connection.execute(query=query, **kwargs)

    @property
    def description(self) -> List[Dict[str, Any]]:
        return self._connection.description

    def fetchall(self) -> List[List]:
        return self._result.fetchall()

    def close(self):
        self._connection.close()


class Connection:

    def __init__(self, dsn: str):
        self._endpoint = dsn
        self._cursor = Cursor(self)

        self._do_connect()

        self.description = None

    @staticmethod
    def serialize(data: Dict[str, Any]) -> str:
        return json.dumps(data)

    @staticmethod
    def serialize_pickle(data: Dict) -> str:
        serialized = pickle.dumps(data)
        encoded_bytes = base64.b64encode(serialized)
        return str(encoded_bytes, "utf-8")

    @staticmethod
    def unserialize(data: str) -> Dict:
        serialized = base64.b64decode(data)
        return pickle.loads(serialized)

    @staticmethod
    def _do_http_request_sync(url: str, method: str = 'GET', headers: Dict = {}, body: str = '',
                              timeout: int = 200) -> str:

        req = XMLHttpRequest.new()
        req.open(method, url, False)
        req.timeout = timeout
        for header, value in enumerate(headers):
            req.setRequestHeader(header, value)
        req.send(body)
        return req.response

    def _do_command(self, command: str, body: str = '', timeout: int = 200) -> Dict[str, Any]:
        url = f'{self._endpoint}/{command}'
        headers = {'Content-Type': 'application/json'}

        response = self._do_http_request_sync(url=url, method='POST', headers=headers, body=body, timeout=timeout)

        return self.unserialize(response)

    def _do_connect(self):
        response = self._do_command(command='connect')
        self._connection_id = response['connection_id']

    def _do_disconnect(self):
        if not self._connection_id:
            return
        body = self.serialize({'connection_id': self._connection_id})
        response = self._do_command(command='disconnect', body=body)
        if response['result'] == 'ok':
            self._connection_id = False

    def _do_query(self, query: str, timeout: int) -> Dict[str, Any]:

        if not self._connection_id:
            self._do_connect()

        body = self.serialize({
            'query': query,
            'connection_id': self._connection_id
        })

        return self._do_command(command='query', body=body)

    def cursor(self) -> Cursor:
        return self._cursor

    def execute(self, query, timeout=10000, *args, **kwargs) -> Result:
        self.description = None
        response = self._do_query(query, timeout)
        if response['result'] == 'ok':
            self.description = response['description']
            return Result(response['rows'])
        else:
            raise Exception('Query Failed')

    def rollback(self):
        pass

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._do_disconnect()


class Connectable:
    pass


class Engine(Connectable):

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._connection = False

    def connect(self) -> Connection:
        self._connection = Connection(self._dsn)
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()


class ResultProxy:
    pass
