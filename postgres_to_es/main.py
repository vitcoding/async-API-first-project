from contextlib import closing
from datetime import datetime, timezone
from time import perf_counter, sleep

import psycopg
from backoff import backoff
from config import DSL, SLEEP_TIME, logger
from data_state import JsonFileStorage, State
from get_data import PostgresExtractor
from load_data import ElasticsearchLoader
from psycopg import ClientCursor
from psycopg.rows import dict_row


def load_from_postgres(pg_connection: psycopg.Connection) -> int:
    """Основная функция загрузки данных из Postgres в ElasticSearch."""

    postgres_extractor = PostgresExtractor(pg_connection)
    elasticsearch_loader = ElasticsearchLoader()

    storage = JsonFileStorage("./data/data_state.json")
    state = State(storage)

    update_time = state.get_state("last_update")
    if update_time is not None:
        logger.info(
            "\nПоследнее время обновления: %s.\n"
            "Будут загружены данные, добавленные после указанного времени.\n",
            update_time,
        )
    else:
        logger.info(
            "\nПоследнее время обновления отсутствует.\n"
            "\nБудут загружены все данные.\n"
        )

    new_update_time = datetime.now(timezone.utc)

    data = postgres_extractor.extract_data(update_time)
    result = elasticsearch_loader.load_data(data)

    if result >= 0:
        state.set_state("last_update", str(new_update_time))
        logger.info(
            "\nПоследнее время обновления изменено: %s.\n",
            new_update_time,
        )

    return result


backoff_wrapper = backoff()


@backoff_wrapper
def main() -> None:
    """Основная функция запуска программы."""

    with closing(
        psycopg.connect(
            **DSL, row_factory=dict_row, cursor_factory=ClientCursor
        )
    ) as pg_connection:
        logger.info("\nЦикл программы запущен\n")
        start_time = perf_counter()

        transfer = load_from_postgres(pg_connection)

        end_time = perf_counter()

    execute_time = end_time - start_time

    if transfer:
        logger.info(
            "\n🎉 Цикл завершен. Всего загружено данных за цикл: %s."
            "\nВремя выполнения: %s\n\n\n",
            transfer,
            execute_time,
        )
    else:
        logger.info(
            "\nОбновленные данные для загрузки отсутствуют."
            "\nЦикл завершен. Время выполнения: %s\n\n\n",
            execute_time,
        )

    sleep(SLEEP_TIME)


if __name__ == "__main__":

    main()
