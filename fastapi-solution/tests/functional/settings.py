import logging
import os

from pydantic.v1 import BaseSettings, Field

# Настройки логера для дебага
format_log = (
    "#%(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s"
)
logging.basicConfig(
    level=logging.DEBUG,
    format=format_log,
)
log = logging.getLogger("DEBUG_LOG")


class BaseTestSettings(BaseSettings):
    es_schema: str = Field(default="http://", env="ELASTIC_SCHEMA")
    es_host: str = Field(default="127.0.0.1", env="ELASTIC_HOST")
    es_port: int = Field(default=9200, env="ELASTIC_PORT")
    es_index: str = "movies"
    es_id_field: str = Field("id", env="ES_ID_FIELD")
    es_index_mapping: dict = Field(
        {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "imdb_rating": {"type": "float"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "genres": {"type": "text"},
                    "directors_names": {"type": "text"},
                    "actors_names": {"type": "text"},
                    "writers_names": {"type": "text"},
                    "directors": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text"},
                        },
                    },
                    "actors": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text"},
                        },
                    },
                    "writers": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "keyword"},
                            "name": {"type": "text"},
                        },
                    },
                }
            }
        }
    )

    redis_schema: str = Field(default="http://", env="REDIS_SСHEMA")
    redis_host: str = Field(default="127.0.0.1", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")

    service_schema: str = Field(default="http://", env="SERVICE_SСHEMA")
    service_host: str = Field(default="127.0.0.1", env="SERVICE_HOST")
    service_port: int = Field(default=8000, env="SERVICE_PORT")

    class Config:
        env_file = "dev.env"
        env_file_encoding = "utf-8"


class TestSettings(BaseTestSettings):
    class Config:
        env_file = "doc.env"
        env_file_encoding = "utf-8"


# For local development: export APP_ENV="dev"
def get_settings() -> BaseSettings:
    environment = os.environ.get("APP_ENV", "docker")
    log.debug("\nEnvironment: '%s'\n", environment)
    if environment == "docker":
        return TestSettings()
    if environment == "dev":
        return BaseTestSettings()
    else:
        os.environ["APP_ENV"] = "docker"
        log.warning(
            "\nUncorrect 'APP_ENV': \n'%s'.\n"
            "The default value has been assigned: 'docker'\n",
            environment,
        )
        return TestSettings()


test_settings = get_settings()

es_url = (
    f"{test_settings.es_schema}{test_settings.es_host}"
    f":{test_settings.es_port}"
)

redis_url = (
    f"{test_settings.redis_schema}{test_settings.redis_host}"
    f":{test_settings.redis_port}"
)

service_url = (
    f"{test_settings.service_schema}{test_settings.service_host}"
    f":{test_settings.service_port}"
)
