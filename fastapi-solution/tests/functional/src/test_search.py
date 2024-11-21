import asyncio
import uuid

import pytest

from core.conftest import (
    aiohttp_session,
    es_check_data,
    es_client,
    es_write_data,
    event_loop,
    make_get_request,
)


async def es_load_data(
    es_write_data, es_check_data, event: asyncio.Event
) -> None:

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

    await es_write_data(bulk_query)

    await es_check_data(event)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star"}, {"status": 200, "length": 50}),
        ({"query": "Mashed potato"}, {"status": 404, "length": 1}),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_search(
    es_write_data, es_check_data, make_get_request, query_data, expected_answer
) -> None:
    event = asyncio.Event()
    await es_load_data(es_write_data, es_check_data, event)
    search_urn = "/api/v1/films/search"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
