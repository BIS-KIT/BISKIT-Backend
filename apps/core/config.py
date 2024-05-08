from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    PROJECT_NAME: str

    ## DataBase
    BISKIT_USER: str
    BISKIT_USER_PW: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    DB_ROOT_PASSWORD: str
    TEST_DB: str
    CORS_ORIGINS: str

    NICKNAME_API: str

    ## Auth
    DOCS_USER: str
    DOCS_PW: str
    SECRET_KEY: str

    ## JWT
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    ## SMTP
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    S3_URL: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    BUCKET_NAME: str

    LOGO_URL: str

    FIRESTORE_URL: str

    REDIS_HOST: str

    ENCODED_KEY: str

    DEBUG: bool

    @property
    def cors_origins_list(self) -> List[str]:
        return self.CORS_ORIGINS.split(",")


settings = Setting()
