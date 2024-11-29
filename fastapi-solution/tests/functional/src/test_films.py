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
from testdata.films import generate_films, index_
from testdata.films_queries import films_list_queries, films_search_queries
from testdata.genres import genre_action
from testdata.genres import index_ as genres_index


@pytest.mark.asyncio(loop_scope="session")
async def test_films(
    es_write_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test film function."""

    es_data = generate_films()
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)
    film_id = es_data[0]["id"]
    film_id_wrong = f"{film_id}none"

    search_urn = f"/api/v1/films/{film_id}"
    status, _, _ = await make_get_request(search_urn)
    key = f"Film: id: {str(film_id)}"
    cashed_data = await redis_get_data(key)
    search_urn_wrong = f"/api/v1/films/{film_id_wrong}"
    status_wrong, _, _ = await make_get_request(search_urn_wrong)
    key_wrong = f"Film: id: {str(film_id_wrong)}"
    cashed_data_wrong = await redis_get_data(key_wrong)

    assert status == HTTPStatus.OK
    assert cashed_data == True
    assert status_wrong == HTTPStatus.NOT_FOUND
    assert cashed_data_wrong == False


@pytest.mark.parametrize("query_data, expected_answer", films_list_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_films_list(
    es_write_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test films list function."""

    await es_write_data(
        genres_index,
        [
            {"_index": genres_index, "_id": row["id"], "_source": row}
            for row in genre_action
        ],
    )
    quantity = 120
    es_data = generate_films(quantity)
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)

    search_urn = "/api/v1/films"
    status, _, body = await make_get_request(search_urn, query_data)
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

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
    assert cashed_data == expected_answer["cashed_data"]


@pytest.mark.parametrize("query_data, expected_answer", films_search_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_films_search(
    es_write_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test films search function."""

    quantity = 120
    es_data = generate_films(quantity)
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)

    search_urn = "/api/v1/films/search"
    status, _, body = await make_get_request(search_urn, query_data)
    query_value = query_data.get("query", None)
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = (
        f"FilmSearch: {query_value}, "
        f"size: {page_size_value}, "
        f"page: {page_number_value}"
    )
    cashed_data = await redis_get_data(key)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
    assert cashed_data == expected_answer["cashed_data"]
