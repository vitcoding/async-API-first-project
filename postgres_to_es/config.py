import logging
import os

from pydantic_settings import BaseSettings

format_log = (
    "#%(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s"
)
logging.basicConfig(
    level=logging.INFO,
    format=format_log,
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    POSTGRES_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SQL_HOST: str
    SQL_PORT: int
    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: int
    batch_size: int = 200
    sleep_time: int = 1000
    tables: tuple[str, ...] = (
        "film_work",
        "genre",
        "person",
        "genre_film_work",
        "person_film_work",
    )
    db_schema: dict[str, str] = {"postgres": "content."}


class SettingsDocker(Settings):
    class Config:
        env_file = "doc.env"


class SettingsDev(Settings):
    class Config:
        env_file = "dev.env"


def get_settings() -> BaseSettings:
    environment = os.environ.get("APP_ENV", "docker")
    logger.debug("\nОкружение: '%s'\n", environment)
    if environment == "docker":
        return SettingsDocker()
    if environment == "dev":
        return SettingsDev()
    else:
        os.environ["APP_ENV"] = "docker"
        logger.warning(
            "\nЗадано некорректное окружение: \n'%s'.\n"
            "Присвоено значение по умолчанию: 'docker'\n",
            environment,
        )
        return SettingsDocker()


settings = get_settings()

DSL = {
    "dbname": settings.POSTGRES_NAME,
    "user": settings.POSTGRES_USER,
    "password": settings.POSTGRES_PASSWORD,
    "host": settings.SQL_HOST,
    "port": settings.SQL_PORT,
}

ES_HOST = settings.ELASTICSEARCH_HOST
ES_PORT = settings.ELASTICSEARCH_PORT

TABLES = settings.tables

DB_SCHEMA = settings.db_schema

BATCH_SIZE = settings.batch_size

SLEEP_TIME = settings.sleep_time
