import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str = "theidfactory_ordini"
    DB_USERNAME: str
    DB_PASSWORD: str

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-5-nano"

    SESSION_TTL_HOURS: int = 24

    # ENV_FILE permette di scegliere il file di ambiente senza toccare .env,
    # es. `ENV_FILE=.env.stage uvicorn app.main:app --reload` (vedi README).
    model_config = {"env_file": os.getenv("ENV_FILE", ".env"), "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
