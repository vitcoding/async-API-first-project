from typing import Any, ClassVar, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class UUIDMix(BaseModel):
    """
    Базовый класс с полем UUID.

    :param id: Уникальный идентификатор объекта.
    """
    id: UUID


class Genre(UUIDMix):
    """
    Модель жанра.

    :param name: Название жанра.
    :param description: Описание жанра.
    """
    name: str
    description: Optional[str]
    _index: ClassVar[str] = 'genres'


class Person(UUIDMix):
    """
    Модель человека.

    :param full_name: Полное имя человека.
    """
    full_name: str = Field(alias='name')
    _index: ClassVar[str] = 'persons'

    class Config(object):
        """Конфигурация модели Person."""
        allow_population_by_field_name = True


class Movie(UUIDMix):
    """Модель фильма."""
    imdb_rating: Optional[float]
    genres: List[str]
    title: str
    description: Optional[str]
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: List[Person]
    actors: List[Person]
    writers: List[Person]
    _index: ClassVar[str] = 'movies'

    @classmethod
    def properties(cls, **kwargs) -> Dict[str, Any]:
        """
        Генерирует свойства для модели на основе схемы.

        :param kwargs: Дополнительные аргументы, передаваемые в схему.
        :return: Словарь свойств с ключами полей и начальными значениями.
        """
        properties: Dict[str, Any] = {}
        for field, value in cls.schema(**kwargs)['properties'].items():
            if value['type'] == 'string':
                properties[field] = ''
            if value['type'] == 'array':
                properties[field] = []
            if value['type'] == 'number':
                properties[field] = 0
        return properties

    @validator('actors', 'writers', 'directors', each_item=True)
    def change_person_field(cls, person: Person) -> Dict:
        """
        Изменяет формат объекта Person для списка актеров и сценаристов.

        :param person: Объект Person для изменения.
        :return: Словарь с идентификатором и именем человека.
        """
        return {'id': person.id, 'name': person.full_name}
