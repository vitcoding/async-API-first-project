from http import HTTPStatus
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.person import PersonService, get_person_service
from services.person_films import (
    PersonFilmListService,
    get_person_film_list_service,
)
from services.persons_search import (
    PersonListSearchService,
    get_person_list_search_service,
)

router = APIRouter()


# Модель ответа API (персона)
class Person(BaseModel):
    id: UUID
    full_name: str
    films: list[dict[str, Any]]


# Модель ответа API (кинопроизведения персоны)
class PersonFilmList(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None


@router.get(
    "/search",
    response_model=List[Person],
    summary="Поиск персон",
    description="Полнотекстовый поиск по персонам",
    response_description="Имя и кинопроизведения персоны",
    tags=["Полнотекстовый поиск"],
)
async def person_list(
    query: str | None = Query(None),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    person_service: PersonListSearchService = Depends(
        get_person_list_search_service
    ),
) -> list:
    persons = await person_service.get_list(query, page_size, page_number)
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="persons not found"
        )
    return [Person(**dict(person)) for person in persons]


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Персона",
    description="Данные по персоне",
    response_description="Имя и кинопроизведения персоны",
    tags=["Персона"],
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person not found"
        )
    return Person(**dict(person))


@router.get(
    "/{person_id}/film",
    response_model=List[PersonFilmList],
    summary="Список кинопроизведений персоны",
    description="Список кинопроизведений персоны",
    response_description="Название и рейтинг киопроизведения",
    tags=["Кинопроизведения персоны"],
)
async def person_film_list(
    person_id: str,
    person_films_service: PersonFilmListService = Depends(
        get_person_film_list_service
    ),
) -> list:
    person_films = await person_films_service.get_by_id(person_id)
    if not person_films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="person films not found"
        )
    return [PersonFilmList(**dict(film)) for film in person_films]
