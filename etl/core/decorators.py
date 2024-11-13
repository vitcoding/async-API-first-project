import time
from functools import wraps
from typing import Any, Callable, Tuple

from core.logger import logger


def backoff(errors: Tuple, start_sleep_time=0.1, factor=2, border_sleep_time=10) -> Callable:
    """
    Декоратор для автоматической обработки ошибок с повторными попытками.

    :param errors: Кортеж исключений, при возникновении которых будет выполняться повторная попытка.
    :param start_sleep_time: Начальное время задержки между попытками (по умолчанию 0.1 секунд).
    :param factor: Коэффициент увеличения времени задержки после каждой неудачной попытки (по умолчанию 2).
    :param border_sleep_time: Максимальное время задержки (по умолчанию 10 секунд).
    :return: Декоратор, который оборачивает функцию и добавляет логику повторных попыток.
    """

    def decorator(func) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = start_sleep_time
            while True:
                try:
                    conn = func(*args, **kwargs)
                except errors as message:
                    logger.error('There is no connection: {0}!'.format(message))
                    if delay < border_sleep_time:
                        delay *= factor  # Увеличиваем задержку на основе фактора
                    logger.error('Reconnecting via {0}.'.format(delay))
                    time.sleep(delay)
                else:
                    return conn

        return wrapper

    return decorator
