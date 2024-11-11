from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.abstracts import AbstractListService


class GenreListService(AbstractListService):

    async def get_list(
        self,
        # sort_field: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Genre]]:

        log.info("\nGetting genres.\n")

        # key = f"{sort_field}, {page_size}, {page_number}"
        key = f"{page_size}, {page_number}"
        genres = await self._get_from_cache(key, "genre", is_list=True)
        if not genres:
            genres = await self._get_list_from_elastic(page_size, page_number)
            # genres = await self._get_list_from_elastic(
            #     sort_field, page_size, page_number
            # )
            if not genres:
                return None

            await self._put_to_cache(key, genres, "genre")

        return genres

    async def _get_list_from_elastic(
        self,
        # sort_field: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Genre]]:

        index_ = "genres"
        docs_total = await self._docs_total(index_)
        pages_total = await self._pages_total(docs_total, page_size)
        page_size = await self._validate_pages(
            docs_total, page_number, pages_total, page_size
        )

        # order = ("asc", "desc")[sort_field.startswith("-")]
        # if order == "desc":
        #     sort_field = sort_field[1:]

        query_body = {
            "size": (page_size),
            "from": (page_number - 1) * page_size,
            # "sort": [
            #     {
            #         sort_field: {"order": order, "missing": "_last"},
            #     }
            # ],
        }

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nGeting genres from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            genres = [Genre(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return genres


@lru_cache()
def get_genre_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreListService:
    return GenreListService(redis, elastic)
