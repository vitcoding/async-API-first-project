import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from core.settings import es_url, log, test_settings
from testdata.es_mapping import MOVIES_MAPPING


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data():

    async def inner(data: list[dict]):
        log.debug("\nes_url: \n%s\n", es_url)
        es_client = AsyncElasticsearch(hosts=[es_url], verify_certs=False)

        index_ = "movies_test"

        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(
            index=test_settings.es_index, **MOVIES_MAPPING
        )

        updated, errors = await async_bulk(client=es_client, actions=data)

        await es_client.close()

        if errors:
            raise Exception("Error writing data to Elasticsearch")

    return inner
