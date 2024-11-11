from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Genre(BaseModel):
    id: UUID | str
    name: str
    description: str | None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = str(self.id)


class GenreRedis(Genre):
    def __post_init__(self):
        if isinstance(self.id, UUID):
            self.id = str(self.id)
