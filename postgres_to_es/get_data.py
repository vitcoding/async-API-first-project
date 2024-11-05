from contextlib import closing
from typing import Generator

import psycopg
from psycopg.rows import dict_row

from config import BATCH_SIZE, DB_SCHEMA, logger


class PostgresExtractor:
    def __init__(
        self,
        pg_connection: psycopg.Connection,
        schema: str = DB_SCHEMA["postgres"],
        batch_size: int = BATCH_SIZE,
    ) -> None:
        self.pg_connection = pg_connection
        self.schema = schema
        self.batch_size = batch_size

    def get_query(self) -> list[str]:
        """Метод получения запроса к БД на список ИД фильмов для извлечения."""

        if self.update_time is None:
            all_films = "SELECT id FROM content.film_work; "
            query_list = [all_films]

        else:
            all_films_updates = (
                f"SELECT id FROM content.film_work "
                f"WHERE modified > '{str(self.update_time)}';"
            )
            all_persons_updates = (
                f"SELECT fw.id FROM content.film_work fw "
                f"LEFT JOIN content.person_film_work pfw "
                f"ON pfw.film_work_id = fw.id "
                f"LEFT JOIN content.person p ON p.id = pfw.person_id "
                f"WHERE p.modified > '{str(self.update_time)}';"
            )

            all_genres_updates = (
                f"SELECT fw.id FROM content.film_work fw "
                f"LEFT JOIN content.genre_film_work gfw "
                f"ON gfw.film_work_id = fw.id "
                f"LEFT JOIN content.genre g ON g.id = gfw.genre_id "
                f"WHERE g.modified > '{str(self.update_time)}';"
            )
            query_list = [
                all_films_updates,
                all_persons_updates,
                all_genres_updates,
            ]
        return query_list

    def get_movies_ids(self) -> Generator[list[str], None, None]:
        """Метод получения ИД фильмов с обновлениями."""
        self.pg_connection.row_factory = dict_row

        with closing(
            self.pg_connection.cursor(row_factory=dict_row)
        ) as pg_cursor:
            logger.debug("\nЗапущено получение ИД фильмов с обновлениями.\n")

            ids_set = set()
            for query in self.get_query():

                pg_cursor.execute(query)
                ids = pg_cursor.fetchall()

                logger.debug("\nСформирован SQL запрос:\n'%s'\n", query)

                ids = set(list(id.values())[0] for id in ids)
                ids_set |= ids

            logger.info(
                "\nИзвлечено ИД фильмов для загрузки: \n%s\n", len(ids_set)
            )

            ids_list = list(ids_set)

            for i in range(0, len(ids_list), self.batch_size):
                batch = ids_list[i:i + self.batch_size]
                logger.debug("\nПартия для извлечения (ИД): \n%s\n", batch)
                yield batch

    def extract_data(
        self,
        update_time: str,
    ) -> Generator[list[dict], None, None]:
        """Основной метод извлечения данных из PostgreSQL."""

        self.update_time = update_time

        for ids in self.get_movies_ids():

            query_ids_list = [repr(id) for id in ids]

            logger.debug(
                "\nПартия для извлечения (ИД): \n%s\n", query_ids_list
            )
            logger.debug(
                "\nКоличество фильмов для извлечения: \n%s\n",
                len(query_ids_list),
            )

            query_ids = ", ".join(query_ids_list)

            self.pg_connection.row_factory = dict_row

            with closing(
                self.pg_connection.cursor(row_factory=dict_row)
            ) as pg_cursor:
                logger.info("\nЗапущено извлечение данных\n")

                query = (
                    f"SELECT "
                    f"fw.id, "
                    f"fw.rating as imdb_rating, "
                    f"g.name as g_genre ,"
                    f"fw.title, "
                    f"fw.description, "
                    f"p.id as p_id, "
                    f"p.full_name as p_name, "
                    f"pfw.role as p_role "
                    f"FROM content.film_work fw "
                    f"LEFT JOIN content.person_film_work pfw "
                    f"ON pfw.film_work_id = fw.id "
                    f"LEFT JOIN content.person p ON p.id = pfw.person_id "
                    f"LEFT JOIN content.genre_film_work gfw "
                    f"ON gfw.film_work_id = fw.id "
                    f"LEFT JOIN content.genre g ON g.id = gfw.genre_id "
                    f"WHERE fw.id IN ({query_ids});"
                )
                pg_cursor.execute(query)

                logger.debug("Сформирован SQL запрос:\n'%s'\n", query)

                batch = pg_cursor.fetchall()
                yield batch
