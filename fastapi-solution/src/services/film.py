from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # Надо будет добавить кэширование
    async def get_film_list(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film]:

        if sort_field.startswith("-"):
            sort_field = sort_field[1:]
            sort_parameters = {"order": "desc"}
        else:
            sort_parameters = {"order": "asc"}

        query_body = {
            "size": page_size,
            "from": (page_number - 1) * page_size,
            "sort": [
                {sort_field: sort_parameters},
            ],
        }

        # Надо будет скорректировать после добавления индексов по жанрам
        if genre_uuid is not None:
            query_body["query"] = {"match": {"genres": "Drama"}}

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            docs = await self.elastic.search(
                index="movies",
                body=query_body,
            )
            films = [Film(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return films

    async def get_by_id(self, film_id: str) -> Optional[Film]:

        log.info("\nЗапрос фильма по id '%s'\n", film_id)

        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            log.info("\nПолучение данных из ElasticSearch\n")
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
