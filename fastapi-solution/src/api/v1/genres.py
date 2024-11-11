from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

# from services.genre import FilmService, get_film_service
from services.genres import GenreListService, get_genre_list_service

router = APIRouter()


# Модель ответа API
class GenreList(BaseModel):
    id: UUID
    name: str
    description: str | None


# class Genre(BaseModel):
#     id: UUID
#     title: str
#     imdb_rating: float | None
#     description: str | None
#     # Надо будет дополнительно скорректировать
#     genres: list
#     # directors_names: list
#     # actors_names: list
#     # writers_names: list
#     directors: list
#     actors: list
#     writers: list


@router.get("")
async def film_list(
    # sort: str | None = Query("-name"),
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    genre_service: GenreListService = Depends(get_genre_list_service),
) -> list:
    genres = await genre_service.get_list(page_size, page_number)
    # genres = await genre_service.get_list(sort, page_size, page_number)
    return [GenreList(**dict(genre)) for genre in genres]


# @router.get("/{film_id}", response_model=Film)
# async def film_details(
#     film_id: str, film_service: FilmService = Depends(get_film_service)
# ) -> Film:
#     film = await film_service.get_by_id(film_id)
#     if not film:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail="film not found"
#         )

#     return Film(**dict(film))
