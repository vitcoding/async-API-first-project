import asyncio
import datetime
import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from ..settings import test_settings

# from tests.functional.settings import test_settings

#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.


async def es_load_data(event: asyncio.Event):
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
    es_client = AsyncElasticsearch(
        hosts=[test_settings.es_host], verify_certs=False
    )

    if await es_client.indices.exists(index=test_settings.es_index):
        await es_client.indices.delete(index=test_settings.es_index)
    await es_client.indices.create(
        index=test_settings.es_index, **test_settings.es_index_mapping
    )

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    await es_client.close()

    if errors:
        raise Exception("Ошибка записи данных в Elasticsearch")

    es_client = AsyncElasticsearch(
        hosts=[test_settings.es_host], verify_certs=False
    )
    while True:
        try:
            document_count = await es_client.count(index="movies")
            count = document_count["count"]
            if count == 60:
                ###
                print(f"\n\ndocument_count: {document_count}\n")
                break
            await asyncio.sleep(0.1)
        except Exception as err:
            ###
            print(err)
            # raise err
    await es_client.close()

    event.set()


async def search_data(event: asyncio.Event):
    await event.wait()
    # 3. Запрашиваем данные из ES по API
    async with aiohttp.ClientSession() as session:
        url = test_settings.service_url + "/api/v1/films/search"
        query_data = {"query": "The Star"}
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

    return status, body


@pytest.mark.asyncio
async def test_search():
    event = asyncio.Event()
    await es_load_data(event)
    status, body = await search_data(event)

    # 4. Проверяем ответ
    assert status == 200
    assert len(body) == 50
