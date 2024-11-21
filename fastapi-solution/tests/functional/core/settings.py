import os

from pydantic.v1 import BaseSettings, Field

from testdata.es_mapping import MOVIES_MAPPING

from .logger import log


class BaseTestSettings(BaseSettings):
    es_schema: str = Field(default="http://", env="ELASTIC_SCHEMA")
    es_host: str = Field(default="127.0.0.1", env="ELASTIC_HOST")
    es_port: int = Field(default=9200, env="ELASTIC_PORT")
    es_index: str = "movies"

    ###
    es_id_field: str = Field("id", env="ES_ID_FIELD")

    ###
    es_index_mapping: dict = Field(MOVIES_MAPPING)

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
            "The default value 'docker' has been assigned.\n",
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
