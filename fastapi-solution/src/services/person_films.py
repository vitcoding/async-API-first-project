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


class PersonFilmListService(AbstractItemService):
    """Класс для работы со списком кинопроизведений персоны"""

    async def get_by_id(self, person_id: str) -> Optional[list[Film]]:
        """Основной метод получения списка кинопроизведений персоны."""

        log.info("\nGetting person '%s'.\n", person_id)

        person_films = await self._get_from_cache(
            str(person_id) + "_films", "film", is_list=True
        )
        if not person_films:
            person_films = await self._get_item_from_elastic(person_id)

            if not person_films:
                return None

            await self._put_to_cache(
                str(person_id) + "_films", person_films, "film"
            )

        return person_films

    async def _get_item_from_elastic(
        self, person_id: str
    ) -> Optional[list[Film]]:
        """Метод получения списка кинопроизведений персоны из elasticsearch."""
        try:
            log.info("\nGetting person from elasticsearch\n")

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
    return PersonFilmListService(redis, elastic)
