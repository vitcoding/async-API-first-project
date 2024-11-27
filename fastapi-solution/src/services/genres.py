from functools import lru_cache
from typing import List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.abstracts import AbstractListService
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService


class GenreListService(AbstractListService):
    """Класс для работы со списком жанров."""

    async def get_list(self, page_size: int, page_number: int) -> List[Genre] | None:
        """Основной метод получения списка жанров."""
        log.info("\nGetting genres.\n")

        key = f"GenreList: size: {page_size}, page: {page_number}"
        genres = await self.get_from_cache(key, "genre", is_list=True)
        if not genres:
            genres = await self._get_list_from_elastic(page_size, page_number)
            if not genres:
                return None

            await self.put_to_cache(key, genres, "genre")

        return genres

    async def _get_list_from_elastic(self, page_size: int, page_number: int) -> List[Genre] | None:
        """Метод получения списка жанров из Elasticsearch."""
        index_ = "genres"
        docs_total = await self.es_service.count(index_)
        pages_total = await self.get_pages_total(docs_total, page_size)
        page_size = await self.validate_pages(docs_total, page_number, pages_total, page_size)

        query_body = {
            "size": page_size,
            "from": (page_number - 1) * page_size,
        }

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nGetting genres from Elasticsearch.\n")
            docs = await self.es_service.elastic.search(index=index_, body=query_body)
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
    """Провайдер GenreListService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return GenreListService(cache_service, es_service)
