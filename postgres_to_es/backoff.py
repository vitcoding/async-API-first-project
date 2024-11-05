from functools import wraps
from time import sleep
from typing import Callable

import elastic_transport
import psycopg

from config import logger


def backoff(
    start_sleep_time: int | float = 0.1,
    factor: int | float = 2,
    border_sleep_time: int | float = 10,
    limit: int = 10,
) -> Callable:

    def func_wrapper(func: Callable) -> Callable:

        @wraps(func)
        def inner(*args, **kwargs) -> None:
            counter = 0
            while True:
                try:
                    func(*args, **kwargs)
                except (
                    psycopg.OperationalError,
                    elastic_transport._exceptions.ConnectionError,
                ) as err:
                    counter += 1
                    logger.error(
                        "Ошибка %s при исполнении цикла программы: \n'%s'.\n",
                        type(err),
                        err,
                    )

                    if counter >= limit:
                        logger.warning(
                            "\nДостигнут лимит (%s) попыток "
                            "подключения с ошибками.\n"
                            "\nПрограмма завершена.\n",
                            limit,
                        )
                        break
                    sleep_time = min(
                        start_sleep_time * (factor**counter), border_sleep_time
                    )
                    sleep(sleep_time)
                except Exception as err:
                    logger.warning(
                        "\nПроизошла непредвиденная ошибка %s: \n'%s'.\n"
                        "\nПрограмма завершена.\n\n",
                        type(err),
                        err,
                    )
                    break

        return inner

    return func_wrapper
