import json
from pyodide import to_js
from js import fetch, Object
from typing import List, Dict, Any


class Result:

    def __init__(self, rows: List):
        self.result = []
        for row in rows:
            self.result.append({key: getattr(row, key) for key in Object.keys(row)})

    def fetchall(self) -> List[Dict[str, Any]]:
        return self.result


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


class Engine:

    def __init__(self, dsn: str):
        self.dsn = dsn

    def connect(self) -> Connection:
        return Connection(self.dsn)

    def close(self):
        pass
