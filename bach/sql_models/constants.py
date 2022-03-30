from enum import Enum
from typing import Union

from sqlalchemy.engine import Dialect, Engine


class NotSet(Enum):
    """
    INTERNAL: Special token used as default value for parameters, to distinguish the default value from
    None for Optional values.
    """
    token = 0


not_set: NotSet = NotSet.token


class DBDialect(Enum):
    """
    Supported database dialects.

    The values are equal to Dialect.name for specific SqlAlchemy Dialect classes e.g.
        DBDialects.POSTGRES.value == PGDialect.name

    Generally we'll use the sqlalchemy.engine.Dialect class to define a certain database type (e.g. when
    passing as a parameter). However, when needing to specify a database type in generic code, then use this
    class. This class hardcodes the values, and thus does not depend on any specific python packages being
    installed. i.e. accessing DBDialect.BIGQUERY works even if the 'sqlalchemy-bigquery' package is not
    installed.
    """
    POSTGRES = 'postgresql'  # value of PGDialect.name
    BIGQUERY = 'bigquery'  # value of BigQueryDialect.name

    def is_dialect(self, dialect_engine: Union[Dialect, Engine]):
        return dialect_engine.name == self.value

    @classmethod
    def from_engine(cls, engine: Engine) -> 'DBDialect':
        return DBDialect(engine.name)

    @classmethod
    def from_dialect(cls, dialect: Dialect) -> 'DBDialect':
        return DBDialect(dialect.name)
