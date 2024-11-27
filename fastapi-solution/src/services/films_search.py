from functools import lru_cache
from typing import List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractListService
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService
from services.es_queries.generation_query_body import generation_query_body


class FilmListSearchService(AbstractListService):
    """Класс для работы с поиском кинопроизведений."""

    async def get_list(
            self,
            query: str | None,
            page_size: int,
            page_number: int,
    ) -> List[Film] | None:
        """Основной метод получения списка кинопроизведений."""
        log.info("\nGetting films.\n")

        key = f"FilmSearch: {query}, size: {page_size}, page: {page_number}"
        films = await self.get_from_cache(key, "film", is_list=True)
        if not films:
            films = await self._get_list_from_elastic(query, page_size, page_number)
            if not films:
                return None

            await self.put_to_cache(key, films, "film")

        return films

    async def _get_list_from_elastic(
            self,
            query: str | None,
            page_size: int,
            page_number: int,
    ) -> List[Film] | None:
        """Метод получения списка кинопроизведений из Elasticsearch."""
        index_ = "movies"
        docs_total = await self.es_service.count(index_)
        pages_total = await self.get_pages_total(docs_total, page_size)
        page_size = await self.validate_pages(docs_total, page_number, pages_total, page_size)

        query_body = generation_query_body(page_size, page_number, query)

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nSearching films from Elasticsearch.\n")
            docs = await self.es_service.elastic.search(index=index_, body=query_body)
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
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return FilmListSearchService(cache_service, es_service)
