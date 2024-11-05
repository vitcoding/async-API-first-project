from dataclasses import dataclass
from uuid import UUID

from validate import validate_data


class IterMixin:
    def __iter__(self):
        """Магический метод для итерируемости данных класса."""

        yield from [
            (attribute, getattr(self, attribute))
            for attribute in self.__match_args__
        ]


class PostInitMixin:
    def __post_init__(self):
        """Метод валидации данных после инициализации."""

        for attribute in self.__match_args__:
            attribute, value = list(
                validate_data({attribute: getattr(self, attribute)}).items()
            )[0]

            setattr(self, attribute, value)


@dataclass
class FilmworkExtract(PostInitMixin, IterMixin):
    id: UUID
    imdb_rating: float
    g_genre: str
    title: str
    description: str
    p_id: UUID
    p_name: str
    p_role: str


@dataclass
class FilmworkTransform(IterMixin):
    id: UUID
    imdb_rating: float
    genres: list
    title: str
    description: str
    directors_names: list
    actors_names: list
    writers_names: list
    directors: list
    actors: list
    writers: list
