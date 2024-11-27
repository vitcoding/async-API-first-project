from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.abstracts import AbstractItemService
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService


class GenreService(AbstractItemService):
    """Класс для работы с жанром."""

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Основной метод получения жанра по id."""
        log.info("\nGetting genre '%s'.\n", genre_id)

        key = f"Genre: id: {genre_id}"
        genre = await self.get_from_cache(key, "genre")
        if not genre:
            genre = await self._get_item_from_elastic(genre_id)
            if not genre:
                return None

            await self.put_to_cache(key, genre, "genre")

        return genre

    async def _get_item_from_elastic(self, genre_id: str) -> Genre | None:
        """Метод получения жанра по id из Elasticsearch."""
        try:
            log.info("\nGetting genre from Elasticsearch.\n")
            doc = await self.es_service.get(index="genres", id=genre_id)
        except NotFoundError:
            return None

        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """Провайдер GenreService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return GenreService(cache_service, es_service)
