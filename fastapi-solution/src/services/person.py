from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.abstracts import AbstractItemService, PersonFilmsMixin
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService
from services.tools.person_films_dict import films_dict


class PersonService(AbstractItemService, PersonFilmsMixin):
    """Класс для работы с персоной."""

    async def get_by_id(self, person_id: str) -> Person | None:
        """Основной метод получения персоны по id."""

        log.info("\nGetting person '%s'.\n", person_id)

        key = f"Person: id: {str(person_id)}"
        person = await self.get_from_cache(key, "person")
        if not person:
            person = await self._get_item_from_elastic(person_id)

            if not person:
                return None
            await self.put_to_cache(key, person, "person")

        return person

    async def _get_item_from_elastic(self, person_id: str) -> Person | None:
        """Метод получения персоны по id из elasticsearch."""
        try:
            log.info("\nGetting person from elasticsearch\n")
            doc = await self.es_service.get(index="persons", id=person_id)

            films = [
                dict(film) for film in await self._get_person_films(person_id)
            ]

            films_person = films_dict(person_id, films)
        except NotFoundError:
            return None

        person = Person(**doc["_source"], films=films_person)

        return person


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    """Провайдер PersonService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return PersonService(cache_service, es_service)
