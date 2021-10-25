Experiment to access a PG db from a jupyter-lite notebook


** installation **
0. Pre-requisites
- have a postgres instance running
- python3

1. first, install python requirements:
```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Start flask PG service
```bash
cd  app
export POSTGRES_PASSWORD=<password here>
flask run
```

3. Build PG wrapper package
```bash
pip wheel . -w jupyter-lite/files
```

4. Build buhtuh package
```bash
cd ../buhtuh
pip wheel . -w jupyter-lite/jupyter-lite/files --no-deps
```


5. init and start jupyterlite:
```bash
cd jupyter-lite
jupyter-lite init
jupyter-lite serve
```

6. Now open a browser and surf to http://localhost:8000
You should now be able to open the `pg wrapper test` notebook, and run a query against the db
