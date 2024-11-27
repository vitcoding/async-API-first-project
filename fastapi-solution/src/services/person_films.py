from functools import lru_cache
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.abstracts import AbstractItemService, PersonFilmsMixin
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService


class PersonFilmListService(AbstractItemService, PersonFilmsMixin):
    """Класс для работы со списком кинопроизведений персоны"""

    async def get_by_id(self, person_id: str) -> list[Film] | None:
        """Основной метод получения списка кинопроизведений персоны."""

        log.info("\nGetting person '%s'.\n", person_id)

        key = f"PersonFilms: id: {str(person_id)}"
        person_films = await self.get_from_cache(key, "film", is_list=True)
        if not person_films:
            person_films = await self._get_item_from_elastic(person_id)

            if not person_films:
                return None

            await self.put_to_cache(key, person_films, "film")

        return person_films

    async def _get_item_from_elastic(
            self, person_id: str
    ) -> list[dict[str, Any]] | None:
        """Метод получения списка кинопроизведений персоны из elasticsearch."""
        try:
            log.info("\nGetting person from elasticsearch.\n")

            person_films = await self._get_person_films(person_id)

        except NotFoundError:
            return None

        return person_films


@lru_cache()
def get_person_film_list_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonFilmListService:
    """Провайдер FilmListService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return PersonFilmListService(cache_service, es_service)
