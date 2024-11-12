from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from services.films import FilmListService, get_film_list_service
from services.films_search import (
    FilmListSearchService,
    get_film_list_search_service,
)

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Модель ответа API
class FilmList(BaseModel):
    id: UUID
    imdb_rating: float | None
    title: str
    # genres: list
    # description: str | None
    # directors_names: list
    # actors_names: list
    # writers_names: list
    # directors: list
    # actors: list
    # writers: list


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
    description: str | None
    # Надо будет дополнительно скорректировать
    genres: list
    # directors_names: list
    # actors_names: list
    # writers_names: list
    directors: list
    actors: list
    writers: list


@router.get("")
async def film_list(
    sort: str | None = Query("-imdb_rating"),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    genre: str = Query(None),
    film_service: FilmListService = Depends(get_film_list_service),
) -> list:
    films = await film_service.get_list(sort, page_size, page_number, genre)
    return [FilmList(**dict(film)) for film in films]


@router.get("/search")
async def search_film_list(
    query: str | None = Query(None),
    # sort: str | None = Query("-imdb_rating"),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    film_service: FilmListSearchService = Depends(
        get_film_list_search_service
    ),
) -> list:
    films = await film_service.get_list(query, page_size, page_number)
    # films = await film_service.get_list(
    #     query, sort, page_size, page_number, genre
    # )
    return [FilmList(**dict(film)) for film in films]


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )

    return Film(**dict(film))
