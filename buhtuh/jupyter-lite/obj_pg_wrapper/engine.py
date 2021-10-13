import json
from pyodide import to_js
from js import fetch, Object, setTimeout
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
        self.queries = {}
        self.query_counter = 1

    def _do_request_sync(self, query: str, query_id: int, timeout: int):

        data = {"query": query}
        body = json.dumps(data)

        headers = Object.fromEntries(to_js({"Content-Type": "application/json"}))
        # let's get it'
        def set_result(data):
            print(f'set result called for {query_id} with {data}')
            self.queries[query_id] = data
            
            print(f'stored data: {self.queries}')
        fetch(self.endpoint, method='POST', headers=headers, body=body).then(lambda resp: resp.json()).then(lambda data: set_result(data))
        
        wait = 1000
        def waiting(self):
            print(f'waiting {self.queries}')
        while True:
            print(f'checking: {self.queries}, looking for {query_id}')
            if len(self.queries[query_id]) > 0:
                break
            setTimeout(waiting(self), wait)
            wait += wait
            
            if wait > timeout:
                print('timeout expired!')
                break



    def execute_sync(self, query, timeout = 10000) -> Result:
        query_id = self.query_counter
        self.query_counter += 1
        print(f'new query: query_id: {query_id}')
        self.queries[query_id] = []
        self._do_request_sync(query, query_id, timeout)
        
        
        
        result = [r for r in self.queries[query_id]]
        del self.queries[query_id]
        return Result(result)


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
        self.connection = False

    def connect(self) -> Connection:
        self.connection = Connection(self.dsn)
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
