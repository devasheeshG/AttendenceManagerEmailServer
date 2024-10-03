# Path: `app/env.py`
# Description: This file contains code to load `.env` file and make a pydantic `BaseSettings` class which can be used to access environment variables in the application.

from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PostgreSQL Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @classmethod
    def get_postgres_uri(cls) -> str:
        return f"postgresql://{cls().POSTGRES_USER}:{cls().POSTGRES_PASSWORD}@{cls().POSTGRES_HOST}:{cls().POSTGRES_PORT}/{cls().POSTGRES_DB}"

    # ACS Configuration
    ACS_EMAIL: str
    ACS_KEY: str
    ACS_ENDPOINT: str
    
    # Application Configuration
    UPDATE_INTERVAL: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
