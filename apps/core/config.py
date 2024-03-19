from typing import List, Optional
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    PROJECT_NAME: str
    BISKIT_USER: str
    BISKIT_USER_PW: str
    POSTGRES_DB: str
    DB_ROOT_PASSWORD: str
    CORS_ORIGINS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    NICKNAME_API: str
    DOCS_USER: str
    DOCS_PW: str
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
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

    @property
    def cors_origins_list(self) -> List[str]:
        return self.CORS_ORIGINS.split(",")

    class Config:
        env_file = ".env"


settings = Setting()
