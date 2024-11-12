from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service
from services.genres import GenreListService, get_genre_list_service

router = APIRouter()


class Genre(BaseModel):
    id: UUID
    name: str
    description: str | None


@router.get(
    "/",
    response_model=List[Genre],
    summary="Список жанров",
    description="Постраничный список жанров",
    response_description="Название и описание жанров",
    tags=["Список жанров"],
)
async def genre_list(
    page_size: int = Query(50, ge=1),
    page_number: int = Query(1),
    genre_service: GenreListService = Depends(get_genre_list_service),
) -> list:
    genres = await genre_service.get_list(page_size, page_number)
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="genres not found"
        )
    return [Genre(**dict(genre)) for genre in genres]


@router.get(
    "/{genre_id}",
    response_model=Genre,
    summary="Жанр",
    description="Данные по жанру",
    response_description="Название и описание жанра",
    tags=["Жанр"],
)
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="genre not found"
        )
    return Genre(**dict(genre))
