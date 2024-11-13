from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.abstracts import AbstractItemService


class GenreService(AbstractItemService):
    """Класс для работы с жанром."""

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Основной метод получения жанра по id."""

        log.info("\nGetting genre '%s'.\n", genre_id)

        key = f"Genre: id: {str(genre_id)}"
        genre = await self._get_from_cache(key, "genre")
        if not genre:
            genre = await self._get_item_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_to_cache(key, genre, "genre")

        return genre

    async def _get_item_from_elastic(self, genre_id: str) -> Genre | None:
        """Метод получения жанра по id из elasticsearch."""
        try:
            log.info("\nGetting genre from elasticsearch\n")
            doc = await self.elastic.get(index="genres", id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    """Провайдер GenreService."""
    return GenreService(redis, elastic)
