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


class FilmListSearchService(AbstractListService):
    """Класс для работы с поиском кинопроизведений."""

    async def get_list(
        self,
        query: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Film]]:
        """Основной метод получения списка кинопроизведений."""

        log.info("\nGetting films.\n")

        key = f"{query}, {page_size}, {page_number}"
        films = await self._get_from_cache(key, "film", is_list=True)
        if not films:
            films = await self._get_list_from_elastic(
                query, page_size, page_number
            )
            if not films:
                return None

            await self._put_to_cache(key, films, "film")

        return films

    async def _get_list_from_elastic(
        self,
        query: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Film]]:
        """Метод получения списка кинопроизведений из elasticsearch."""

        index_ = "movies"
        docs_total = await self._docs_total(index_)
        pages_total = await self._pages_total(docs_total, page_size)
        page_size = await self._validate_pages(
            docs_total, page_number, pages_total, page_size
        )

        query_body = {
            "size": (page_size),
            "from": (page_number - 1) * page_size,
        }

        if query is not None:
            query_body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",
                        "description^2",
                        "genres" "directors_names",
                        "actors_names",
                        "writers_names",
                    ],
                }
            }

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nSearching films from elasticsearch\n")
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
def get_film_list_search_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmListSearchService:
    """Провайдер FilmListSearchService."""
    return FilmListSearchService(redis, elastic)
