from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from services.films import FilmListService, get_film_list_service
from services.films_search import (
    FilmListSearchService,
    get_film_list_search_service,
)

router = APIRouter()


# Модель ответа API (список кинопроизведений)
class FilmList(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None


# Модель ответа API (кинопроизведение)
class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list
    actors: list
    writers: list
    directors: list


@router.get(
    "/",
    response_model=List[FilmList],
    summary="Список кинопроизведений",
    description="Постраничный список кинопроизведениям",
    response_description="Название и рейтинг киопроизведения",
    tags=["Список кинопроизведений"],
)
async def film_list(
    sort: str | None = Query("-imdb_rating"),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    genre: str = Query(None),
    film_service: FilmListService = Depends(get_film_list_service),
) -> list:
    films = await film_service.get_list(sort, page_size, page_number, genre)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="films not found"
        )
    return [FilmList(**dict(film)) for film in films]


@router.get(
    "/search",
    response_model=List[Film],
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг киопроизведения",
    tags=["Полнотекстовый поиск"],
)
async def search_film_list(
    query: str | None = Query(None),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    film_service: FilmListSearchService = Depends(
        get_film_list_search_service
    ),
) -> list:
    films = await film_service.get_list(query, page_size, page_number)
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="films not found"
        )
    return [FilmList(**dict(film)) for film in films]


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Кинопроизведение",
    description="Данные по кинопроизведению",
    response_description="Название, рейтинг, оисание, жанры "
    + "и роли кинопроизведения",
    tags=["Кинопроизведение"],
)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )
    return Film(**dict(film))
