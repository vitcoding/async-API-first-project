import asyncio
from typing import AsyncGenerator, Callable, Generator

import aiohttp
import pytest_asyncio

from core.abstract import CacheClient, SearchClient
from core.elasticsearch_client import ElasticsearchClient
from core.redis_client import RedisCacheClient
from core.settings import es_url, log, redis_url, service_url, test_settings
from testdata.es_mapping import ES_MAPPING
from utils.backoff import backoff


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Async loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client() -> AsyncGenerator:
    """Elasticsearch connection fixture."""
    es_client = ElasticsearchClient(hosts=[es_url], verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client() -> AsyncGenerator:
    """Redis connection fixture."""
    redis_client = RedisCacheClient(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture(name="aiohttp_session", scope="session")
async def aiohttp_session() -> AsyncGenerator:
    """API connection fixture."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(es_client: SearchClient) -> Callable:
    """Elasticsearch write data fixture."""

    @backoff()
    async def inner(index_: str, data: list[dict]) -> None:
        log.debug("\nes_url: \n%s\n", es_url)

        if await es_client.index_exists(index=index_):
            await es_client.delete_index(index=index_)
        await es_client.create_index(index=index_, settings=ES_MAPPING[index_])

        updated, errors = await es_client.bulk_write(
            actions=data, refresh="wait_for"
        )

        if errors:
            raise Exception("Error writing data to Elasticsearch")

    return inner


@pytest_asyncio.fixture(name="redis_get_data")
def redis_get_data(redis_client: CacheClient) -> Callable:
    """Redis get data fixture."""

    @backoff()
    async def inner(key: str) -> None:
        log.debug("\nredis_url: \n%s\n", redis_url)

        try:
            cached_data = await redis_client.get(key)

        except:
            Exception("Error reading data from Redis")

        result = True if cached_data is not None else False
        return result

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_session) -> Callable:
    """API request fixture."""

    @backoff()
    async def inner(
        service_urn: str, query_data: dict = None
    ) -> tuple[int | dict]:
        service_uri = service_url + service_urn
        log.debug("\nservice_uri: \n%s\n", service_uri)

        if query_data is None:
            query_data = {}

        async with aiohttp_session.get(
            service_uri, params=query_data
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

        return status, headers, body

    return inner
