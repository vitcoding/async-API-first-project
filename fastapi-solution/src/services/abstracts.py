import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any

from elasticsearch import NotFoundError
from fastapi import HTTPException

from core.logger import log
from models.film import Film
from models.genre import Genre
from models.person import Person
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService
from services.es_queries import common, persons_in_films


class PageNumberPagination:
    async def get_pages_total(self, docs_total: int, page_size: int) -> int:
        """Определение количества страниц."""
        pages_total = (docs_total + page_size - 1) // page_size
        return pages_total

    async def validate_pages(
            self,
            docs_total: int,
            page_number: int,
            pages_total: int,
            page_size: int,
    ) -> int:
        """Метод валидации количества страниц."""

        if page_number < 1 or page_number > pages_total:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="page not found"
            )
        if page_number == pages_total:
            page_size_last = docs_total - (page_size * (pages_total - 1))
            return page_size_last
        return page_size


class AbstractService(ABC):
    """Абстрактный базовый класс для сервисов."""

    def __init__(self, cache_service: CacheService, es_service: ElasticsearchService):
        self.cache_service = cache_service
        self.es_service = es_service
        self._models = {
            "film": Film,
            "genre": Genre,
            "person": Person,
        }

    async def get_from_cache(self, key: str, model: str, is_list: bool = False) -> Any:
        """Получение данных из кеша."""
        object_ = self._models[model]
        data = await self.cache_service.get(key)
        if not data:
            return None

        if is_list:
            collection = [object_(**row) for row in json.loads(data.decode())]
            return collection
        return object_.parse_raw(data)

    async def put_to_cache(self, key: str, data: list | Film, model: str) -> None:
        """Сохранение данных в кеш."""
        object_ = self._models[model]
        if isinstance(data, list):
            serialized_data = json.dumps(
                [dict(object_(**dict(item))) for item in data]
            )
        else:
            serialized_data = data.json()

        await self.cache_service.set(key, serialized_data)


class PersonFilmsMixin(AbstractService):
    async def _get_person_films(self, person_id: str) -> list[dict[str, Any]]:
        """Метод сборки кинопроизведений по персоне."""

        index_ = "movies"

        query_body = common.get_query()
        query_body["query"] = persons_in_films.get_query(person_id)
        try:
            log.info("\nGeting films from elasticsearch.\n")
            docs = await self.es_service.search(
                index=index_,
                body=query_body,
            )
            films_person = [Film(**doc["_source"]) for doc in docs]

        except NotFoundError:
            return None

        log.debug("\nfilms_person: \n%s\n", films_person)

        return films_person


class AbstractListService(AbstractService, PageNumberPagination):
    """Абстрактный класс для работы со списком сущностей."""

    @abstractmethod
    async def get_list(self, *args, **kwargs) -> Any:
        pass


class AbstractItemService(AbstractService):
    """Абстрактный класс для работы с одной сущностью."""

    @abstractmethod
    async def get_by_id(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def _get_item_from_elastic(
            self,
            *args,
            **kwargs,
    ) -> Any:
        """Абстрактный метод получения элемента по id из elasticsearch."""
        pass
