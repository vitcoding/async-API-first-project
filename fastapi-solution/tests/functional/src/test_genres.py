from http import HTTPStatus

import pytest

from core.conftest import (
    aiohttp_session,
    es_client,
    es_write_data,
    event_loop,
    make_get_request,
    redis_client,
    redis_get_data,
)
from testdata.genres import generate_genres, index_
from testdata.genres_queries import genres_queries


@pytest.mark.asyncio(loop_scope="session")
async def test_genres(
    es_write_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test genre function."""

    es_data = generate_genres()
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)
    genre_id = es_data[0]["id"]
    genre_id_wrong = f"{genre_id}none"

    search_urn = f"/api/v1/genres/{genre_id}"
    status, _, _ = await make_get_request(search_urn)
    key = f"Genre: id: {str(genre_id)}"
    cashed_data = await redis_get_data(key)
    search_urn_wrong = f"/api/v1/genres/{genre_id_wrong}"
    status_wrong, _, _ = await make_get_request(search_urn_wrong)
    key_wrong = f"Genre: id: {str(genre_id_wrong)}"
    cashed_data_wrong = await redis_get_data(key_wrong)

    assert status == HTTPStatus.OK
    assert cashed_data == True
    assert status_wrong == HTTPStatus.NOT_FOUND
    assert cashed_data_wrong == False


@pytest.mark.parametrize("query_data, expected_answer", genres_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_genres_list(
    es_write_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test genres list function."""

    quantity = 10
    es_data = generate_genres(quantity)
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)

    search_urn = "/api/v1/genres"
    status, _, body = await make_get_request(search_urn, query_data)
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = f"GenreList: size: {page_size_value}, page: {page_number_value}"
    cashed_data = await redis_get_data(key)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
    assert cashed_data == expected_answer["cashed_data"]
