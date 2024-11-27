from functools import lru_cache
from typing import List

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractListService
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService
from services.es_queries import common


class FilmListService(AbstractListService):
    """Класс для работы со списком кинопроизведений."""

    async def get_list(
            self,
            sort_field: str | None,
            page_size: int,
            page_number: int,
            genre_uuid: str | None,
    ) -> List[Film] | None:
        """Основной метод получения списка кинопроизведений."""
        log.info("\nGetting films.\n")

        key = (
            f"FilmList: sort: {sort_field}, size: {page_size}, "
            f"page: {page_number}, genre_uuid: {genre_uuid}"
        )
        films = await self.get_from_cache(key, "film", is_list=True)
        if not films:
            films = await self._get_list_from_elastic(
                sort_field, page_size, page_number, genre_uuid
            )
            if not films:
                return None

            await self.put_to_cache(key, films, "film")

        return films

    async def _get_list_from_elastic(
            self,
            sort_field: str | None,
            page_size: int,
            page_number: int,
            genre_uuid: str | None,
    ) -> List[Film] | None:
        """Метод получения списка кинопроизведений из Elasticsearch."""

        index_ = "movies"
        docs_total = await self.es_service.count(index_)
        pages_total = await self.get_pages_total(docs_total, page_size)
        page_size = await self.validate_pages(docs_total, page_number, pages_total, page_size)
        page_size = min(page_size, docs_total - (page_size * (page_number - 1)))

        query_body = common.get_query(page_size, page_number, sort_field)

        if genre_uuid is not None:
            genre_name = await self._get_genre_name_from_id(genre_uuid)
            if genre_name is None:
                return None

            query_body["query"] = {"match": {"genres": genre_name}}

        log.info("\nquery_body: \n%s\n", query_body)

        docs = await self.es_service.search(index_, query_body)
        if not docs:
            return None

        films = [Film(**doc["_source"]) for doc in docs]
        return films

    async def _get_genre_name_from_id(self, genre_id: str):
        """Метод получения названия жанра по id."""
        index_ = "genres"
        query_body = common.get_query()
        query_body["query"] = {"match": {"id": genre_id}}

        docs = await self.es_service.search(index_, query_body)
        if not docs:
            return None

        genre_name = docs[0]["_source"]["name"]
        return genre_name


@lru_cache()
def get_film_list_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmListService:
    """Провайдер FilmListService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return FilmListService(cache_service, es_service)
