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

    @property
    def cors_origins_list(self) -> List[str]:
        return self.CORS_ORIGINS.split(",")

    class Config:
        env_file = ".env"


settings = Setting()
