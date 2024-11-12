import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from redis.asyncio import Redis

from core.config import log
from models.film import Film
from models.genre import Genre
from models.person import Person
from services.es_queries import common, persons_in_films
from services.tools.person_films_dict import films_dict

# CACHE_EXPIRE_IN_SECONDS = 60 * 5
CACHE_EXPIRE_IN_SECONDS = 1


class AbstractService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self._models = {
            "film": Film,
            "genre": Genre,
            "person": Person,
        }

    async def _get_from_cache(
        self,
        key: str,
        model: str,
        is_list: bool = False,
    ) -> Optional[list | Film]:

        object_ = self._models[model]

        if is_list:

            data = await self.redis.get(key)
            if not data:
                return None

            log.info("\nGetting data from redis.\n")
            collection = [object_(**row) for row in json.loads(data.decode())]
            return collection

        else:
            data = await self.redis.get(key)
            if not data:
                return None

            log.info("\nGetting data from redis.\n")
            item = object_.parse_raw(data)
            return item

    async def _put_to_cache(
        self, key: str, data: list | Film, model: str
    ) -> None:

        object_ = self._models[model]

        if isinstance(data, list):
            serialized_data = json.dumps(
                [dict(object_(**dict(item))) for item in data]
            )
            await self.redis.set(key, serialized_data, CACHE_EXPIRE_IN_SECONDS)
            log.info("\nThe data is placed in redis.\n")

        else:
            await self.redis.set(key, data.json(), CACHE_EXPIRE_IN_SECONDS)
            log.info("\nThe data is placed in redis.\n")

    async def _get_person_films(self, person_id: str) -> list[dict[str, Any]]:
        index_ = "movies"

        query_body = common.get_query()
        query_body["query"] = persons_in_films.get_query(person_id)

        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            films = [
                dict(Film(**doc["_source"])) for doc in docs["hits"]["hits"]
            ]
        except NotFoundError:
            return None

        films_person = films_dict(person_id, films)

        log.debug("\nfilms_person: \n%s\n", films_person)

        return films_person


class AbstractListService(AbstractService):

    async def _docs_total(self, index_: str) -> int:
        data = await self.elastic.count(
            index=index_,
        )
        docs_total = int(data["count"])
        return docs_total

    async def _pages_total(self, docs_total: int, page_size: int) -> int:
        pages_total_float = docs_total / page_size
        pages_total = int(pages_total_float)
        if pages_total < pages_total_float:
            pages_total += 1
        return pages_total

    async def _validate_pages(
        self,
        docs_total: int,
        page_number: int,
        pages_total: int,
        page_size: int,
    ) -> int:
        if page_number < 1 or page_number > pages_total:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="page not found"
            )
        if page_number == pages_total:
            page_size_last = docs_total - (page_size * (pages_total - 1))
            return page_size_last
        return page_size

    @abstractmethod
    async def get_list(
        self,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass

    @abstractmethod
    async def _get_list_from_elastic(
        sself,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass


class AbstractItemService(AbstractService):

    @abstractmethod
    async def get_by_id(
        self,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass

    @abstractmethod
    async def _get_item_from_elastic(
        sself,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass
