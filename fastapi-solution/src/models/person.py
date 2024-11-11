from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Person(BaseModel):
    id: UUID | str
    full_name: str
    films: list[dict[str, Any]]

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = str(self.id)


class PersonRedis(Person):
    def __post_init__(self):
        if isinstance(self.id, UUID):
            self.id = str(self.id)
