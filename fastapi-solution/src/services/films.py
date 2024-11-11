from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractListService


class FilmListService(AbstractListService):

    async def get_list(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> Optional[list | Film]:

        log.info("\nGetting films.\n")

        key = f"{sort_field}, {page_size}, {page_number}, {genre_uuid}"
        films = await self._get_from_cache(key, "film", is_list=True)
        if not films:
            films = await self._get_list_from_elastic(
                sort_field, page_size, page_number, genre_uuid
            )
            if not films:
                return None
            await self._put_to_cache(key, films)

        return films

    async def _get_list_from_elastic(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film]:

        index_ = "movies"
        docs_total = await self._docs_total(index_)
        pages_total = await self._pages_total(docs_total, page_size)
        page_size = await self._validate_pages(
            docs_total, page_number, pages_total, page_size
        )

        order = ("asc", "desc")[sort_field.startswith("-")]
        if order == "desc":
            sort_field = sort_field[1:]

        query_body = {
            "size": (page_size),
            "from": (page_number - 1) * page_size,
            "sort": [
                {
                    sort_field: {"order": order, "missing": "_last"},
                }
            ],
        }

        # Надо будет скорректировать после добавления индексов по жанрам
        if genre_uuid is not None:
            query_body["query"] = {"match": {"genres": "Drama"}}

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            films = [Film(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return films


@lru_cache()
def get_film_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmListService:
    return FilmListService(redis, elastic)
