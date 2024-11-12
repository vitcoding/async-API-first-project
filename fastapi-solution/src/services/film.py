from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractItemService


class FilmService(AbstractItemService):
    """Класс для работы с кинопроизведением"""

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Основной метод получения кинопроизведения по id."""

        log.info("\nGetting film '%s'.\n", film_id)

        film = await self._get_from_cache(str(film_id), "film")
        if not film:
            film = await self._get_item_from_elastic(film_id)
            if not film:
                return None
            await self._put_to_cache(str(film_id), film, "film")

        return film

    async def _get_item_from_elastic(self, film_id: str) -> Optional[Film]:
        """Метод получения кинопроизведения по id из elasticsearch."""

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
    """Провайдер FilmService."""
    return FilmService(redis, elastic)
