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
from testdata.films import generate_films
from testdata.films_queries import films_list_queries, films_search_queries
from testdata.genres import genre_action


async def es_load_data(
    es_write_data,
    es_check_data,
    event: asyncio.Event,
    quantity: int,
    return_ids: bool = False,
) -> None | list[str]:
    """Async function for loading data to Elasticsearch."""

    index_ = "movies"
    es_data = generate_films(quantity)

    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]

    await es_write_data(index_, bulk_query)

    await es_check_data(index_, event, quantity)

    if return_ids:
        films_ids = [row["id"] for row in es_data]
        return films_ids
    return None


@pytest.mark.asyncio(loop_scope="session")
async def test_films(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test film function."""

    event = asyncio.Event()
    quantity = 5
    film_ids = await es_load_data(
        es_write_data, es_check_data, event, quantity, return_ids=True
    )
    if len(film_ids) > 0:
        film_id = film_ids[0]

    search_urn = f"/api/v1/films/{film_id}"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 200
    key = f"Film: id: {str(film_id)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == True

    film_id_wrong = f"{film_id}none"
    search_urn = f"/api/v1/films/{film_id_wrong}"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 404
    key = f"Film: id: {str(film_id_wrong)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == False


@pytest.mark.parametrize("query_data, expected_answer", films_list_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_films_list(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test films list function."""

    await es_write_data(
        "genres",
        [
            {"_index": "genres", "_id": row["id"], "_source": row}
            for row in genre_action
        ],
    )

    event = asyncio.Event()
    quantity = 120
    await es_load_data(es_write_data, es_check_data, event, quantity)

    search_urn = "/api/v1/films"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]

    sort_field_value = query_data.get("sort_field", "-imdb_rating")
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    genre_uuid_value = query_data.get("genre", None)
    key = (
        f"FilmList: sort: {sort_field_value}, "
        f"size: {page_size_value}, "
        f"page: {page_number_value}, "
        f"genre_uuid: {genre_uuid_value}"
    )
    cashed_data = await redis_get_data(key)
    assert cashed_data == expected_answer["cashed_data"]


@pytest.mark.parametrize("query_data, expected_answer", films_search_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_films_search(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test films search function."""

    event = asyncio.Event()
    quantity = 120
    await es_load_data(es_write_data, es_check_data, event, quantity)

    search_urn = "/api/v1/films/search"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]

    query_value = query_data.get("query", None)
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = (
        f"FilmSearch: {query_value}, "
        f"size: {page_size_value}, "
        f"page: {page_number_value}"
    )
    cashed_data = await redis_get_data(key)
    assert cashed_data == expected_answer["cashed_data"]
