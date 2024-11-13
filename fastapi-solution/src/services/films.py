from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractListService
from services.es_queries import common


class FilmListService(AbstractListService):
    """Класс для работы со списком кинопроизведений."""

    async def get_list(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film] | None:
        """Основной метод получения списка кинопроизведений."""

        log.info("\nGetting films.\n")

        key = (
            f"FilmList: sort: {sort_field}, size: {page_size}, "
            f"page: {page_number}, genre_uuid: {genre_uuid}"
        )
        films = await self._get_from_cache(key, "film", is_list=True)
        if not films:
            films = await self._get_list_from_elastic(
                sort_field, page_size, page_number, genre_uuid
            )
            if not films:
                return None

            await self._put_to_cache(key, films, "film")

        return films

    async def _get_list_from_elastic(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film] | None:
        """Метод получения списка кинопроизведений из elasticsearch."""

        index_ = "movies"
        docs_total = await self._docs_total(index_)
        pages_total = await self._pages_total(docs_total, page_size)
        page_size = await self._validate_pages(
            docs_total, page_number, pages_total, page_size
        )

        query_body = common.get_query(page_size, page_number, sort_field)

        if genre_uuid is not None:
            genre_name = await self._get_genre_name_from_id(genre_uuid)
            if genre_name is None:
                return None

            query_body["query"] = {"match": {"genres": genre_name}}

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

    async def _get_genre_name_from_id(self, genre_id):
        """Метод получения названия жанра по id"""
        index_ = "genres"
        query_body = common.get_query()
        query_body["query"] = {"match": {"id": genre_id}}
        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            if not docs["hits"]["hits"]:
                return None

        except NotFoundError:
            return None

        genre_name = docs["hits"]["hits"][0]["_source"]["name"]

        return genre_name


@lru_cache()
def get_film_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmListService:
    """Провайдер FilmListService."""
    return FilmListService(redis, elastic)
