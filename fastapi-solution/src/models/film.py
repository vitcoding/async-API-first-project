from typing import Any

from pydantic import BaseModel

# from uuid import UUID


class Film(BaseModel):
    # Надо будет добавить трансформацию в кэш для id (пока str)
    id: str
    imdb_rating: float | None
    genres: list[str] | None
    title: str
    description: str | None
    directors_names: list[str] | None
    actors_names: list[str] | None
    writers_names: list[str] | None
    directors: list[dict[str, Any]] | None
    actors: list[dict[str, Any]] | None
    writers: list[dict[str, Any]] | None
