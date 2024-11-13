import time
from datetime import datetime

from pytz import timezone

from core.config import ELASTIC_PAR, POSTGRES_PAR, REDIS_PAR
from core.logger import logger
from db.db import con_elastic, con_postgres, con_redis
from models.models import Genre, Movie, Person
from services import extract, load, transform
from services.state import State, JsonStorage


def run_etl(postgres: extract.PostgresExtractor, data: transform.DataTransform, elastic: load.ElasticLoader,
            state: State):
    """
    Выполняет ETL процесс: извлечение данных из PostgreSQL, трансформацию и загрузку в Elasticsearch.

    :param postgres: Экстрактор для получения обновлений из PostgreSQL.
    :param data: Объект для трансформации данных.
    :param elastic: Загрузчик для отправки данных в Elasticsearch.
    :param state: Объект состояния для отслеживания времени последнего обновления.
    """
    timestamp = state.read_state('last_updated', datetime.min)
    for table, rows in postgres.get_updates(timestamp):
        if table == 'genre':
            elastic.bulk_insert(Genre, rows)
        if table == 'person':
            elastic.bulk_insert(Person, rows)
        for row in postgres.get_film_work_ids(table, rows):
            data.collector('movie_ids', row['id'])
    for movies in data.batcher('movie_ids'):
        for row in postgres.get_movie_data(movies.keys()):
            data.parser(row, movies.get(row['id']))
        elastic.bulk_insert(Movie, movies.values())


def postgres_to_elastic(postgres, elasticsearch, redis):
    """
    Запускает процесс передачи данных из PostgreSQL в Elasticsearch с использованием Redis для состояния.

    :param postgres: Соединение с PostgreSQL.
    :param elasticsearch: Соединение с Elasticsearch.
    :param redis: Соединение с Redis для хранения состояния.
    """
    state = State(JsonStorage('state.json'))
    while True:
        try:
            run_etl(
                extract.PostgresExtractor(postgres),
                transform.DataTransform(redis),
                load.ElasticLoader(elasticsearch),
                state,
            )
        except extract.UpdatesNotFoundError:
            logger.info('There are no updates.')
        else:
            logger.info('There are updates!')
            state.write_state('last_updated', datetime.now(tz=timezone('Europe/Moscow')))
        finally:
            logger.info('Repeat the request in 1 minute.')
            time.sleep(60)


def main():
    """
    Основная функция, которая устанавливает соединения с базами данных и запускает процесс передачи данных.
    """
    with con_postgres(**POSTGRES_PAR) as postgres_conn:
        with con_redis(**REDIS_PAR) as redis_conn:
            with con_elastic(**ELASTIC_PAR) as elastic_conn:
                postgres_to_elastic(postgres_conn, elastic_conn, redis_conn)


if __name__ == '__main__':
    main()
