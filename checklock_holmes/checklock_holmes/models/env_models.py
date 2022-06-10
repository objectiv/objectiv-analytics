from pydantic import BaseModel, Field


class BaseDBEnvModel(BaseModel):
    dsn: str

    def dict(self, **kwargs):
        return {
            field_name.upper(): value
            for field_name, value in super().dict(**kwargs).items()
        }


class BigQueryEnvModel(BaseDBEnvModel):
    google_application_credentials: str = Field(None, alias='credentials_path')
