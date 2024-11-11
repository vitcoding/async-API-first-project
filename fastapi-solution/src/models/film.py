from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    # Надо будет добавить трансформацию в кэш для id (пока str)
    id: UUID
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
