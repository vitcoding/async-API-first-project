from typing import Generator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from config import ES_HOST, ES_PORT, logger
from es_schema import es_settings
from transform_data import TransformData


class ElasticsearchLoader:

    def load_data(
        self,
        data: Generator[list[dict], None, None],
    ) -> int:
        """Метод загрузки данных в ElasticSearch."""

        logger.info("\nЗапущена загрузка данных.\n")

        es_client = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}/")

        transform = TransformData()

        index_name = "movies"
        settings = es_settings
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name, body=settings)
            logger.debug("\nИндекс '%s' успешно создан.\n", index_name)

        counter = 0
        actions = []
        for sources in data:

            actions = []
            transformed_sorces = transform.transform_batch(sources)
            for source in transformed_sorces:
                action = {
                    "_op_type": "index",
                    "_index": index_name,
                    "_id": source["id"],
                    "_source": source,
                }

                actions.append(action)
                counter += 1

            logger.debug("\nЗагружаемые данные: \n%s\n", actions)

            bulk(es_client, actions=actions)

            logger.info("\nЗагружено данных за цикл:  %s\n", counter)

        return counter
