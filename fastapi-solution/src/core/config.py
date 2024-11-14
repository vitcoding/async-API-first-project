import os
from logging import config as logging_config

from pydantic.v1 import BaseSettings, Field

from core.logger import LOGGING


class Settings(BaseSettings):
    project_name: str = Field(default="movies", env="PROJECT_NAME")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    elastic_schema: str = Field(default="http://", env="ELASTIC_SCHEMA")
    elastic_host: str = Field(default="127.0.0.1", env="ELASTICSEARCH_HOST")
    elastic_port: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env="BASE_DIR",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Настройки логирования
logging_config.dictConfig(LOGGING)

settings = Settings()
