from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractItemService
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService


class FilmService(AbstractItemService):
    """Класс для работы с кинопроизведением."""

    async def get_by_id(self, film_id: str) -> Film | None:
        """Основной метод получения кинопроизведения по id."""

        log.info("\nGetting film '%s'.\n", film_id)

        key = f"Film: id: {str(film_id)}"
        film = await self.get_from_cache(key, "film")
        if not film:
            film = await self._get_item_from_elastic(film_id)
            if not film:
                return None
            await self.put_to_cache(key, film, "film")

        return film

    async def _get_item_from_elastic(self, film_id: str) -> Film | None:
        """Метод получения кинопроизведения по id из elasticsearch."""

        try:
            log.info("\nGetting film from elasticsearch.\n")
            doc = await self.es_service.get(index="movies", id=film_id)
        except NotFoundError:
            return None

        return Film(**doc["_source"])


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    """Провайдер FilmService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return FilmService(cache_service, es_service)
