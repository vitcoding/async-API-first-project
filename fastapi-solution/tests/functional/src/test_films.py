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
from testdata.films import generate_films


async def es_load_data(
    es_write_data, es_check_data, event: asyncio.Event
) -> None:

    index_ = "movies"
    quantity = 120
    es_data = generate_films(quantity)

    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]

    await es_write_data(index_, bulk_query)

    await es_check_data(index_, event, quantity)


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        # # films_list
        # ({}, {"status": 200, "length": 50}),
        # ({"sort": "imdb_rating"}, {"status": 200, "length": 50}),
        # ({"page_size": 30}, {"status": 200, "length": 30}),
        # ({"page_size": 0}, {"status": 422, "length": 1}),
        # ({"page_number": 2}, {"status": 200, "length": 50}),
        # ({"page_number": 3}, {"status": 200, "length": 20}),
        # ({"page_number": 4}, {"status": 404, "length": 1}),
        # (
        #     {"genre": "6c162475-c7ed-4461-9184-001ef3d9f26e"},
        #     {"status": 200, "length": 50},
        # ),
        # ########## error
        # (
        #     {"genre": "Drama"},
        #     {"status": 200, "length": 2},
        # ),
        # ##########
        # (
        #     {
        #         "sort": "-imdb_rating",
        #         "page_size": 30,
        #         "page_number": 3,
        #         "genre": "6c162475-c7ed-4461-9184-001ef3d9f26e",
        #     },
        #     {"status": 200, "length": 30},
        # ),
        # # films_search
        ({"query": "The Star"}, {"status": 200, "length": 50}),
        ({"query": "Mashed potato"}, {"status": 404, "length": 1}),
        # (
        #     {"query": "The Star", "page_size": 50, "page_number": 0},
        #     {"status": 404, "length": 1},
        # ),
        # (
        #     {"query": "The Star", "page_size": 50, "page_number": 1},
        #     {"status": 200, "length": 50},
        # ),
        # (
        #     {"query": "The Star", "page_size": 50, "page_number": 3},
        #     {"status": 200, "length": 20},
        # ),
        # (
        #     {"query": "The Star", "page_size": 50, "page_number": 4},
        #     {"status": 404, "length": 1},
        # ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_films(
    es_write_data, es_check_data, make_get_request, query_data, expected_answer
) -> None:
    event = asyncio.Event()
    await es_load_data(es_write_data, es_check_data, event)

    search_urn = "/api/v1/films/search"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
