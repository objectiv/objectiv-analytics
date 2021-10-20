from obj_pg_wrapper.engine import Engine


def create_engine(dsn):

    print(f'connecting to {dsn}')

    engine = Engine(dsn)

    return engine


def sqlalchemy():
    print('stub')

