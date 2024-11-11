from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractItemService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(AbstractItemService):

    async def get_by_id(self, film_id: str) -> Optional[Film]:

        log.info("\nGetting film '%s'.\n", film_id)

        film = await self._get_from_cache(str(film_id), "film")
        if not film:
            film = await self._get_item_from_elastic(film_id)
            if not film:
                return None
            await self._put_to_cache(str(film_id), film)

        return film

    async def _get_item_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            log.info("\nGetting film from elasticsearch\n")
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
