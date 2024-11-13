from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from elasticsearch import Elasticsearch
from redis import Redis
from pydantic import BaseSettings, Field


def con_elastic(host: str, port: int) -> Elasticsearch:
    """
    Создает соединение с Elasticsearch.

    :param host: Хост Elasticsearch.
    :param port: Порт Elasticsearch.
    :return: Объект Elasticsearch.
    """
    return Elasticsearch(host=host, port=port)


class ElasticSettings(BaseSettings):
    """
    Настройки для подключения к Elasticsearch.

    :param host: Хост Elasticsearch (по умолчанию 'localhost').
    :param port: Порт Elasticsearch (по умолчанию 9200).
    """
    host: str = Field(default='elasticsearch', env='ELASTICSEARCH_HOST')
    port: int = Field(default=9200, env='ELASTICSEARCH_PORT')


@contextmanager
def con_postgres(**dsn) -> Iterator[_connection]:
    """
    Контекстный менеджер для подключения к PostgreSQL.

    :param dsn: Параметры подключения к базе данных PostgreSQL.
    :yield: Соединение с базой данных PostgreSQL.
    """
    conn = psycopg2.connect(**dsn)
    conn.cursor_factory = DictCursor
    yield conn
    conn.close()


class PostgresSettings(BaseSettings):
    """
    Настройки для подключения к PostgreSQL.

    :param dbname: Имя базы данных (по умолчанию 'movies_database').
    :param user: Имя пользователя для подключения (по умолчанию 'postgres').
    :param password: Пароль для подключения (по умолчанию 'postgres').
    :param host: Хост PostgreSQL (по умолчанию 'localhost').
    :param port: Порт PostgreSQL (по умолчанию 5432).
    :param options: Дополнительные параметры подключения (по умолчанию '-c search_path=content').
    """
    dbname: str = Field(default='movies_db', env='POSTGRES_DB')
    user: str = Field(default='postgres', env='POSTGRES_USER')
    password: str = Field(default='secret', env='POSTGRES_PASSWORD')
    host: str = Field(default='localhost', env='SQL_HOST')
    port: int = Field(default=5432, env='SQL_PORT')
    options: str = Field(default='-c search_path=content')


def con_redis(db: int, host: str, port: int) -> Redis:
    """
    Создает соединение с Redis.

    :param db: Номер базы данных Redis.
    :param host: Хост Redis.
    :param port: Порт Redis.
    :return: Объект Redis.
    """
    return Redis(db=db, host=host, port=port)


class RedisSettings(BaseSettings):
    """
    Настройки для подключения к Redis.

    :param db: Номер базы данных Redis (по умолчанию 0).
    :param host: Хост Redis (по умолчанию 'localhost').
    :param port: Порт Redis (по умолчанию 6379).
    """
    db: int = Field(default=0)
    host: str = Field(default='redis', env='REDIS_HOST')
    port: int = Field(default=6379, env='REDIS_PORT')
