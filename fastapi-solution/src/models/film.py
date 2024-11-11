from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Film(BaseModel):
    id: UUID | str
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

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = str(self.id)


class FilmRedis(Film):
    def __post_init__(self):
        if isinstance(self.id, UUID):
            self.id = str(self.id)


# class FilmPerson(BaseModel):
#     id: UUID | str
#     roles: list[str] | None

#     def __post_init__(self):
#         if isinstance(self.id, str):
#             self.id = str(self.id)
