from fastapi import APIRouter

from api.v1 import films, genres, persons

router = APIRouter()

router.include_router(films.router, prefix="/v1/films")
router.include_router(genres.router, prefix="/v1/genres")
router.include_router(persons.router, prefix="/v1/persons")
