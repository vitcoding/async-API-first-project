import time

from redis import Redis

from core.logger import log
from core.settings import test_settings


class RedisConnectionError(Exception):
    pass


def wait_for_redis(
    host: str,
    port: int,
    interval: float | int = 1.0,
    timeout: float | int | None = 100,
) -> None:
    """Redis waiting connection function."""

    start_time = time.time()
    attempts = 1

    redis_client = Redis(host=host, port=port)
    while True:
        log.debug("\nRedis connection attempt: %s\n", attempts)
        if redis_client.ping():
            log.info("\nRedis has been connected.\n")
            break
        elif time.time() - start_time > timeout:
            raise RedisConnectionError(
                "Redis connection timeout limit has been exceeded."
            )
        else:
            attempts += 1
            time.sleep(interval)


if __name__ == "__main__":

    wait_for_redis(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
