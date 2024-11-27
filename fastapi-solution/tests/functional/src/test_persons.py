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
from testdata.films import person_in_films
from testdata.persons import generate_persons
from testdata.persons_queries import persons_search_queries
from utils.backoff import backoff


@backoff()
async def es_load_data(
    es_write_data,
    es_check_data,
    event: asyncio.Event,
    quantity: int,
    return_ids: bool = False,
) -> None | list[str]:
    """Async function for loading data to Elasticsearch."""

    index_ = "persons"
    es_data = generate_persons(quantity)

    bulk_query = [
        {"_index": index_, "_id": row["id"], "_source": row} for row in es_data
    ]

    await es_write_data(index_, bulk_query)
    await es_check_data(index_, event, quantity)

    if return_ids:
        person_ids = [row["id"] for row in es_data]
        return person_ids
    return None


@pytest.mark.asyncio(loop_scope="session")
async def test_person(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test person function."""

    event = asyncio.Event()
    quantity = 5
    person_ids = await es_load_data(
        es_write_data, es_check_data, event, quantity, return_ids=True
    )
    if person_ids is not None and len(person_ids) > 0:
        person_id = person_ids[0]

    search_urn = f"/api/v1/persons/{person_id}"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 200
    key = f"Person: id: {str(person_id)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == True

    person_id_wrong = f"{person_id}none"
    search_urn = f"/api/v1/persons/{person_id_wrong}"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 404
    key = f"Person: id: {str(person_id_wrong)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == False


@pytest.mark.asyncio(loop_scope="session")
async def test_person_films(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
) -> None:
    """Test person function."""

    event = asyncio.Event()
    quantity = 5
    person_ids = await es_load_data(
        es_write_data, es_check_data, event, quantity, return_ids=True
    )
    if person_ids is not None and len(person_ids) > 0:
        person_id = person_ids[0]

    person_id = person_in_films["id"]
    search_urn = f"/api/v1/persons/{person_id}/film"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 200
    key = f"PersonFilms: id: {str(person_id)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == True

    person_id_wrong = f"{person_id}none"
    search_urn = f"/api/v1/persons/{person_id_wrong}"
    status, _, _ = await make_get_request(event, search_urn)
    assert status == 404
    key = f"PersonFilms: id: {str(person_id_wrong)}"
    cashed_data = await redis_get_data(key)
    assert cashed_data == False


@pytest.mark.parametrize("query_data, expected_answer", persons_search_queries)
@pytest.mark.asyncio(loop_scope="session")
async def test_persons_search(
    es_write_data,
    es_check_data,
    make_get_request,
    redis_get_data,
    query_data,
    expected_answer,
) -> None:
    """Test persons search function."""

    event = asyncio.Event()
    quantity = 10
    await es_load_data(es_write_data, es_check_data, event, quantity)

    search_urn = "/api/v1/persons/search"
    status, _, body = await make_get_request(event, search_urn, query_data)

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]

    query_value = query_data.get("query", None)
    page_size_value = query_data.get("page_size", 50)
    page_number_value = query_data.get("page_number", 1)
    key = (
        f"PersonSearch: {query_value}, "
        f"size: {page_size_value}, "
        f"page: {page_number_value}"
    )
    cashed_data = await redis_get_data(key)
    assert cashed_data == expected_answer["cashed_data"]
