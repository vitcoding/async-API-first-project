import asyncio
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from core.logger import log
from core.settings import es_url, redis_url, service_url, test_settings
from utils.conftest import es_check_data, es_client, es_write_data, event_loop

#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.


async def es_load_data(
    es_write_data, es_check_data, event: asyncio.Event
) -> None:
    # 1. Генерируем данные для ES
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.5,
            "genres": ["Action", "Sci-Fi"],
            "title": "The Star",
            "description": "New World",
            "directors_names": ["Stan"],
            "actors_names": ["Ann", "Bob"],
            "writers_names": ["Ben", "Howard"],
            "directors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
            ],
            "actors": [
                {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
                {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
            ],
            "writers": [
                {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
                {
                    "id": "b45bd7bc-2e16-46d5-b125-983d356768c6",
                    "name": "Howard",
                },
            ],
        }
        for _ in range(60)
    ]

    bulk_query = [
        {"_index": "movies", "_id": row["id"], "_source": row}
        for row in es_data
    ]

    # 2. Загружаем данные в ES
    await es_write_data(bulk_query)

    await es_check_data(event)


async def search_data(event: asyncio.Event, query_data: dict) -> tuple[str]:
    await event.wait()
    log.debug("\nservice_url: \n%s\n", service_url)

    # 3. Запрашиваем данные из ES по API
    async with aiohttp.ClientSession() as session:
        url = service_url + "/api/v1/films/search"
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

    return status, body


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star"}, {"status": 200, "length": 50}),
        ({"query": "Mashed potato"}, {"status": 404, "length": 1}),
    ],
)
@pytest.mark.asyncio
async def test_search(
    es_write_data, es_check_data, query_data, expected_answer
) -> None:
    event = asyncio.Event()
    await es_load_data(es_write_data, es_check_data, event)
    status, body = await search_data(event, query_data)

    # 4. Проверяем ответ
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
