import asyncio
from typing import AsyncGenerator, Callable, Generator

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from core.settings import es_url, log, redis_url, service_url, test_settings
from testdata.es_mapping import MOVIES_MAPPING


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Async loop fixture."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client() -> AsyncGenerator:
    """Elasticsearch connection fixture."""
    es_client = AsyncElasticsearch(hosts=[es_url], verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client() -> AsyncGenerator:
    """Redis connection fixture."""
    redis_client = Redis(
        host=test_settings.redis_host, port=test_settings.redis_port
    )
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(name="aiohttp_session", scope="session")
async def aiohttp_session() -> AsyncGenerator:
    """API connection fixture."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(es_client: AsyncElasticsearch) -> Callable:
    """Elasticsearch write data fixture."""

    async def inner(index_: str, data: list[dict]) -> None:
        log.debug("\nes_url: \n%s\n", es_url)

        if await es_client.indices.exists(index=index_):
            await es_client.indices.delete(index=index_)
        await es_client.indices.create(index=index_, **MOVIES_MAPPING)

        updated, errors = await async_bulk(client=es_client, actions=data)

        if errors:
            raise Exception("Error writing data to Elasticsearch")

    return inner


@pytest_asyncio.fixture(name="es_check_data")
def es_check_data(es_client: AsyncElasticsearch) -> Callable:
    """Elasticsearch check data fixture."""

    async def inner(index_: str, event: asyncio.Event, quantity: int) -> None:

        while True:
            try:
                document_count = await es_client.count(index=index_)
                count = document_count["count"]
                if count == quantity:
                    log.debug("\ndocument_count: \n%s\n", document_count)
                    break
                await asyncio.sleep(0.1)
            except Exception as err:
                log.error(
                    "\nError %s: \n'%s'.\n",
                    type(err),
                    err,
                )

        event.set()

    return inner


@pytest_asyncio.fixture(name="redis_get_data")
def redis_get_data(redis_client: Redis) -> Callable:
    """Redis get data fixture."""

    async def inner(key: str) -> None:
        log.debug("\nredis_url: \n%s\n", redis_url)

        try:
            cached_data = await redis_client.get(key)

        except:
            cached_data = None
            # Exception("Error reading data from Redis")

        result = True if cached_data is not None else False
        return result

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_session) -> Callable:
    """API request fixture."""

    async def inner(
        event: asyncio.Event, service_urn: str, query_data: dict = None
    ) -> tuple[int | dict]:

        await event.wait()

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
