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
from testdata.films import person_in_films
from testdata.persons import generate_persons, index_
from testdata.persons_queries import persons_search_queries


@pytest.mark.asyncio(loop_scope="session")
async def test_person(
    es_write_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test person function."""

    es_data = generate_persons()
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)
    person_id = es_data[0]["id"]
    person_id_wrong = f"{person_id}none"

    search_urn = f"/api/v1/persons/{person_id}"
    status, _, _ = await make_get_request(search_urn)
    key = f"Person: id: {str(person_id)}"
    cashed_data = await redis_get_data(key)
    search_urn_wrong = f"/api/v1/persons/{person_id_wrong}"
    status_wrong, _, _ = await make_get_request(search_urn_wrong)
    key_wrong = f"Person: id: {str(person_id_wrong)}"
    cashed_data_wrong = await redis_get_data(key_wrong)

    assert status == HTTPStatus.OK
    assert cashed_data == True
    assert status_wrong == HTTPStatus.NOT_FOUND
    assert cashed_data_wrong == False


@pytest.mark.asyncio(loop_scope="session")
async def test_person_films(
    es_write_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test person function."""

    es_data = generate_persons()
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)
    person_id = person_in_films["id"]
    person_id_wrong = f"{person_id}none"

    search_urn = f"/api/v1/persons/{person_id}/film"
    status, _, _ = await make_get_request(search_urn)
    key = f"PersonFilms: id: {str(person_id)}"
    cashed_data = await redis_get_data(key)
    search_urn_wrong = f"/api/v1/persons/{person_id_wrong}"
    status_wrong, _, _ = await make_get_request(search_urn_wrong)
    key_wrong = f"PersonFilms: id: {str(person_id_wrong)}"
    cashed_data_wrong = await redis_get_data(key_wrong)

    assert status == HTTPStatus.OK
    assert cashed_data == True
    assert status_wrong == HTTPStatus.NOT_FOUND
    assert cashed_data_wrong == False


@pytest.mark.parametrize("query_data, expected_answer", persons_search_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_persons_search(
    es_write_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test persons search function."""

    quantity = 10
    es_data = generate_persons(quantity)
    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]
    await es_write_data(index_, bulk_query)

    search_urn = "/api/v1/persons/search"
    status, _, body = await make_get_request(search_urn, query_data)
    query_value = query_data.get("query", None)
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = (
        f"PersonSearch: {query_value}, "
        f"size: {page_size_value}, "
        f"page: {page_number_value}"
    )
    cashed_data = await redis_get_data(key)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]
    assert cashed_data == expected_answer["cashed_data"]
