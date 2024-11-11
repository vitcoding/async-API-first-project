from abc import ABC, abstractmethod
from asyncio import sleep
from http import HTTPStatus
from typing import Any, Optional

from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException
from redis.asyncio import Redis

from core.config import log
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class AbstractService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

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
    async def get_film_list(
        self,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass

    async def _get_films_from_elastic(
        sself,
        *args,
        **kwargs,
    ) -> Optional[list | Film]:
        pass

    async def _get_from_cache(
        self,
        key: str,
        model: str,
        is_list: bool = False,
    ) -> Optional[list | Film]:
        if is_list:
            models = {
                "film": Film,
                # After models add
                "genre": "Genre",
                "person": "Person",
            }
            object_ = models[model]

            data = await self.redis.lrange(key, 0, -1)
            if not data:
                return None

            collection = [object_.parse_raw(row) for row in data]
            return collection
        else:
            data = await self.redis.get(key)
            if not data:
                return None

            item = object_.parse_raw(data)
            return item

    async def _put_to_cache(
        self,
        key: str,
        data: list | Film,
    ) -> None:

        if isinstance(data, list):
            await self.redis.delete(key)
            for item in data:
                await self.redis.rpush(
                    key,
                    item.json(),
                )
            while True:
                try:
                    await self.redis.setex(
                        key,
                        FILM_CACHE_EXPIRE_IN_SECONDS,
                    )
                except TypeError as err:
                    log.info(
                        "\nError '%s': \n%s\n",
                        type(err),
                        err,
                    )
                if bool(await self.redis.exists(key)):
                    log.info("\nAn array key created.\n")
                    break
                await sleep(0.1)
        else:
            await self.redis.set(
                key, data.json(), FILM_CACHE_EXPIRE_IN_SECONDS
            )
