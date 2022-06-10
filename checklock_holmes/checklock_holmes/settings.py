from typing import Dict

from pydantic import BaseSettings

from checklock_holmes.models.env_models import BaseDBEnvModel, BigQueryEnvModel
from checklock_holmes.utils.supported_engines import SupportedEngine


class Settings(BaseSettings):
    pg_db: BaseDBEnvModel
    bq_db: BigQueryEnvModel

    class Config:
        env_file = './.env'
        env_file_enconding = 'utf-8'
        env_nested_delimiter = '__'

    @property
    def _engine_env_var_mapping(self) -> Dict[SupportedEngine, BaseDBEnvModel]:
        return {
            SupportedEngine.POSTGRES: self.pg_db,
            SupportedEngine.BIGQUERY: self.bq_db,
        }

    def get_env_variables(self, engine: SupportedEngine) -> Dict[str, str]:
        return self._engine_env_var_mapping[engine].dict()


settings = Settings()
