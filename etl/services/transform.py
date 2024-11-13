from dataclasses import dataclass
from typing import Any, Dict, Iterator

from redis import Redis
from redis.exceptions import ConnectionError

from core.config import BATCH_SIZE, PostgresRow
from core.decorators import backoff
from models.models import Movie, Person


@dataclass
class DataTransform(object):
    redis: Redis

    @backoff(errors=(ConnectionError,))
    def collector(self, key: str, film_work_id: str):
        """
        Собирает идентификатор произведения и добавляет его в множество Redis.

        :param key: Ключ, под которым будет храниться множество идентификаторов.
        :param film_work_id: Идентификатор произведения для добавления.
        """
        self.redis.sadd(key, film_work_id)

    @backoff(errors=(ConnectionError,))
    def batcher(self, key: str) -> Iterator[Dict[str, Any]]:
        """
        Генерирует пакеты идентификаторов произведений из множества Redis.

        :param key: Ключ множества идентификаторов в Redis.
        :return: Итератор, который возвращает словарь с идентификаторами произведений и их свойствами.
        """
        cursor = '0'
        while cursor != 0:
            cursor, data = self.redis.sscan(key, cursor=cursor, count=BATCH_SIZE)  # type: ignore[assignment, arg-type]
            yield {
                movie_id.decode(): Movie.properties() for movie_id in data
            }
        self.redis.delete(key)

    def parser(self, row: PostgresRow, movie: Dict):
        """
        Парсит данные из строки PostgreSQL и обновляет словарь произведения.

        :param row: Строка данных из PostgreSQL.
        :param movie: Словарь, представляющий произведение, которое нужно обновить.
        """
        if not movie['id']:
            movie['id'] = row['id']
            movie['title'] = row['title']
            movie['description'] = row['description']
            movie['imdb_rating'] = row['rating']
        movie.update(self.add_person(row, movie) if row['person_id'] else {})
        movie.update(self.add_genre(row, movie) if row['genre_name'] else {})

    def add_person(self, row: PostgresRow, movie: Dict) -> Dict:
        """
        Добавляет информацию о человеке (режиссере, актере и т.д.) в словарь произведения.

        :param row: Строка данных из PostgreSQL, содержащая информацию о человеке.
        :param movie: Словарь, представляющий произведение, в которое добавляется информация о человеке.
        :return: Словарь с обновленной информацией о людях, связанных с произведением.
        """
        role = '{role}s'.format(role=row['role'])
        role_names = '{role}s_names'.format(role=row['role'])
        persons_list = movie.get(role, [])
        person_names_list = movie.get(role_names, [])
        person = Person(id=row['person_id'], full_name=row['full_name'])
        if person not in persons_list:
            persons_list.append(person)
            person_names_list.append(person.full_name)
        return {role: persons_list, role_names: person_names_list}

    def add_genre(self, row: PostgresRow, movie: Dict) -> Dict:
        """
        Добавляет информацию о жанре в словарь произведения.

        :param row: Строка данных из PostgreSQL, содержащая информацию о жанре.
        :param movie: Словарь, представляющий произведение, в которое добавляется информация о жанре.
        :return: Словарь с обновленной информацией о жанрах, связанных с произведением.
        """
        genre_names_list = movie.get('genres', [])
        if row['genre_name'] not in genre_names_list:
            genre_names_list.append(row['genre_name'])
        return {'genres': genre_names_list}
