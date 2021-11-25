# Ideas on what workflows to support

problems:
- Do we want to have placeholders, e.g. for 'last 30 days', that we can fill in later?

```python

df = from_table(engine, 'example', index=['city_id'])
db = DashBoard()
# ... operations on df
db.add(df, 'savepoint1', type='view')  # maybe we should call this differently, or have a function on df for it (materialize?)
# ... more operations on df
db.add(df, 'usage_data', type='view')
# ... more operations on df
db.add(df, 'conversion_data', type='table')

# get back to first savepoint
df = db.get('savepoint1')

# TODO: add variable references

# <Skip this part>
db.save('dashboard.json')
db = DashBoard.from_file('dashboard.json')
df_from_file = db.get('savepoint1')
assert df.to_pandas.to_list() == df_from_file.to_pandas.to_list()  # we can serialize and deserialize in a way that we get the same results etc.
assert df != df_from_file  # But getting exact same files is probably hard to do
# </Skip this part>

# Get a list of sql statements (Create tables, create views)
sql_statements: List[str] = db.to_sql()

# Write as dbt project
export_as_dbt_project(db, 'output/directory/project_name/')
export_as_metabase_project(db, db_url='')
export_as_grafana_project(db, db_url='')
export_as_redash_project(db, db_url='')
```



Some other ideas
```python
# a short cut for loading the dashboard file and adding a savepoint
save_df(df, 'dashboard.json', 'savepoint1')
# get back to first savepoint
df = load_df('dashboard.json', 'savepoint1')
```