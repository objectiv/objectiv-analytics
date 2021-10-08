import obj_pg_wrapper

engine = obj_pg_wrapper.create_engine(dsn='bier')

conn = engine.connect()

result = conn.execute('SELECT * FROM data LIMIT 10')

for row in result.fetchall():
    print(f'got row {row}')

