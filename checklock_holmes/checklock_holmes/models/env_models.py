"""
Copyright 2022 Objectiv B.V.
"""
from typing import Optional

from pydantic import BaseModel, Field


class BaseEnvModel(BaseModel):
    _PREFIX = ''

    def dict(self, **kwargs):
        """
        Adds prefix to environment variables names if the model has one.
        """
        return {
            (f'{self._PREFIX}_{field_name}' if self._PREFIX else field_name).upper(): value
            for field_name, value in super().dict(**kwargs).items()
            if field_name != '_PREFIX'
        }


class BaseDBEnvModel(BaseEnvModel):
    dsn: Optional[str] = None


class BigQueryEnvModel(BaseDBEnvModel):
    google_application_credentials: Optional[str] = Field(None, alias='credentials_path')


class MetaBaseEnvModel(BaseEnvModel):
    _PREFIX = 'metabase'

    url: str
    web_url: str
    username: str
    password: str
    dashboard_id: str
    collection_id: str


DEFAULT_METABASE_ENV = MetaBaseEnvModel(
    url="http://localhost:3000",
    web_url="http://localhost:3000",
    username="demo@objectiv.io",
    password="metabase1",
    dashboard_id='1',  # 1-model-hub
    database_id='2',  # objectiv database
    collection_id='2',  # 2-object
)
