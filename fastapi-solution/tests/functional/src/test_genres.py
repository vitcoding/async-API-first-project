import asyncio

import pytest

from core.conftest import (
    aiohttp_session,
    es_check_data,
    es_client,
    es_write_data,
    event_loop,
    make_get_request,
    redis_client,
    redis_get_data,
)
from testdata.genres import generate_genres


async def es_load_data(
    es_write_data,
    es_check_data,
    event: asyncio.Event,
    quantity: int,
    return_ids: bool = False,
) -> None | list[str]:
    """Async function for loading data to Elasticsearch."""

    index_ = "genres"
    es_data = generate_genres(quantity)

    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]

    await es_write_data(index_, bulk_query)

    await es_check_data(index_, event, quantity)

    if return_ids:
        genres_ids = [row["id"] for row in es_data]
        return genres_ids
    return None


@pytest.mark.asyncio(loop_scope="session")
async def test_genres(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test genre function."""

    event = asyncio.Event()
    quantity = 5
    genre_ids = await es_load_data(
        es_write_data, es_check_data, event, quantity, return_ids=True
    )
    if len(genre_ids) > 0:
        genre_id = genre_ids[0]

    search_urn = f"/api/v1/genres/{genre_id}"
    status, _, body = await make_get_request(event, search_urn)
    assert status == 200
    key = f"Genre: id: {str(genre_id)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == True

    genre_id_wrong = f"{genre_id}none"
    search_urn = f"/api/v1/genres/{genre_id_wrong}"
    status, _, body = await make_get_request(event, search_urn)
    assert status == 404
    key = f"Genre: id: {str(genre_id_wrong)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == False


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({}, {"status": 200, "length": 10, "cashed_data": True}),
        (
            {"page_size": 7},
            {"status": 200, "length": 7, "cashed_data": True},
        ),
        ({"page_size": 0}, {"status": 422, "length": 1, "cashed_data": False}),
        (
            {"page_number": 2},
            {"status": 404, "length": 1, "cashed_data": False},
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_genres_list(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test genres list function."""

    event = asyncio.Event()
    quantity = 10
    await es_load_data(es_write_data, es_check_data, event, quantity)

    search_urn = "/api/v1/genres"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]

    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = f"GenreList: size: {page_size_value}, page: {page_number_value}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == expected_answer["cashed_data"]
