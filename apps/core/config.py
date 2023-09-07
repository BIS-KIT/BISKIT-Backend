from typing import List, Optional
from pydantic import BaseSettings


class Setting(BaseSettings):
    BISKIT_USER: str
    BISKIT_USER_PW: str
    POSTGRES_DB: str
    DB_ROOT_PASSWORD: str
    CORS_ORIGINS: List[str]

    class Config:
        env_file = ".env"


settings = Setting()
