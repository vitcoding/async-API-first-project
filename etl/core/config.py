from typing import Type, Union

from psycopg2.extras import DictRow

from db.db import ElasticSettings, PostgresSettings, RedisSettings
from models.models import Genre, Movie, Person

ELASTIC_PAR = ElasticSettings(_env_file='.env').dict()

POSTGRES_PAR = PostgresSettings(_env_file='.env').dict()

REDIS_PAR = RedisSettings(_env_file='.env').dict()

BATCH_SIZE = 100

PostgresRow = DictRow

Schemas = Union[Type[Genre], Type[Person], Type[Movie]]
