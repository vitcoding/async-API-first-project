from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# import models.film
from services.film import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах


# Модель ответа API
class Film(BaseModel):
    id: UUID
    imdb_rating: float
    genres: list
    title: str
    description: str | None
    # directors_names: list
    # actors_names: list
    # writers_names: list
    # directors: list
    # actors: list
    # writers: list


# @router.get("/", response_model=Film)
@router.get("/")
async def film_list(
    film_service: FilmService = Depends(get_film_service),
) -> list:
    films = await film_service.get_film_list()
    return [Film(**dict(film)) for film in films]


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: str, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами,
        # которые содержат enum
        # # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="film not found"
        )

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description,
    # которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики
    # и формирования ответов API,
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    # print(film)
    # for k, v in dict(film).items():
    #     print(f"{k} :    {v}")

    # return film
    return Film(**dict(film))
    # return Film(id=film.id, title=film.title)
