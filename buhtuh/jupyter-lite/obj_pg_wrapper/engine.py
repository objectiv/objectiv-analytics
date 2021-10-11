import json
from pyodide import to_js
from js import fetch, Object
from typing import List, Dict, Any

"""
simple http/json based wrapper to remotely run pg queries

TODO:
- *__make synchronous__*
- fix sessions /cookies for transactions
- send close connection on close of connection (__exit__ / close())
- proper typing (serialization is JSON for now (UUID / Timestamps / JSON))
- probably lots of other stuff
"""

class Result:

    def __init__(self, rows: List):
        self.rows = rows

    def fetchall(self) -> List[List]:
        result = []
        for row in self.rows:
            result.append([getattr(row, key) for key in Object.keys(row)])

        return result
    
    def fetchall_dict(self) -> List[Dict[str, Any]]:
        result = []
        for row in self.rows:
            result.append({key: getattr(row, key) for key in Object.keys(row)})

        return result
    

class Connection:

    def __init__(self, dsn: str):
        self.endpoint = dsn

    async def _do_request(self, query: str) -> List:

        data = {"query": query}
        body = json.dumps(data)

        headers = Object.fromEntries(to_js({"Content-Type": "application/json"}))
        response = await fetch(self.endpoint, method='POST', headers=headers, body=body)

        return await response.json()

    async def execute(self, query) -> Result:
        result = await self._do_request(query)
        return Result(result)


    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        # TODO: implement closing connection / transaction server-side
        pass

class Engine:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection = Null

    def connect(self) -> Connection:
        self.connection = Connection(self.dsn)
        return self.connection()

    def close(self):
        self.connection.close()
