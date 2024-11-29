import logging
import logging.config
import time

import yaml
from elasticsearch import Elasticsearch

from core.logger import log
from core.settings import es_url


class ESConnectionError(Exception):
    pass


def wait_for_elasticsearch(
    host: str,
    interval: float | int = 2,
    timeout: float | int | None = 100,
) -> None:
    """Elasticsearch waiting connection function."""

    start_time = time.time()
    attempts = 1

    es_client = Elasticsearch(hosts=[host])
    while True:
        log.debug("\nElasticsearch connection attempt: %s\n", attempts)
        if es_client.ping():
            log.info("\nElasticsearch has been connected.\n")
            break
        elif timeout is not None and time.time() - start_time > timeout:
            raise ESConnectionError(
                "Elasticsearch connection timeout limit has been exceeded."
            )
        else:
            attempts += 1
            time.sleep(interval)


if __name__ == "__main__":
    with open(f"utils/logging_wait_for_es.ini", "rt") as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)

    wait_for_elasticsearch(es_url)
