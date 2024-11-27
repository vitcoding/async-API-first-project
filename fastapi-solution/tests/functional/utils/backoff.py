import asyncio
from functools import wraps
from typing import Callable

import aiohttp
import elastic_transport
from aiohttp import client_exceptions

from core.logger import log


def backoff(
    start_sleep_time: int | float = 0.1,
    factor: int | float = 2,
    border_sleep_time: int | float = 10,
    limit: int = 10,
    exception_list: tuple[Exception] = (
        elastic_transport._exceptions.ConnectionError,
        aiohttp.ClientOSError,
        aiohttp.ServerDisconnectedError,
        client_exceptions.ClientConnectorError,
        client_exceptions.ContentTypeError,
    ),
) -> Callable:
    """The connection recovery waiting decorator."""

    def func_wrapper(func: Callable) -> Callable:

        @wraps(func)
        async def inner(*args, **kwargs) -> None:
            counter = 0

            while True:
                try:
                    return await func(*args, **kwargs)
                except exception_list as err:
                    counter += 1
                    log.error("\nError %s: \n'%s'.\n", type(err), err)
                    log.debug("\nCounter: %s'.\n", counter)

                    if counter >= limit:
                        log.warning(
                            "\nThe limit (%s) of connection attempts "
                            "with errors has been reached.\n",
                            limit,
                        )
                        raise KeyboardInterrupt(
                            "The tests failed due to connection problems."
                        )
                    sleep_time = min(
                        start_sleep_time * (factor**counter), border_sleep_time
                    )
                    await asyncio.sleep(sleep_time)
                except Exception as err:
                    log.warning(
                        "\nAn unexpected error %s: \n'%s'.\n", type(err), err
                    )
                    raise KeyboardInterrupt(
                        "The tests failed due to connection problems."
                    )

        return inner

    return func_wrapper
