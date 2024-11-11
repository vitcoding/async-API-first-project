from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.abstracts import AbstractItemService


class PersonService(AbstractItemService):

    async def get_by_id(self, person_id: str) -> Optional[Person]:

        log.info("\nGetting person '%s'.\n", person_id)

        person = await self._get_from_cache(str(person_id), "person")
        if not person:
            person = await self._get_item_from_elastic(person_id)
            if not person:
                return None
            await self._put_to_cache(str(person_id), person, "person")

        return person

    async def _get_item_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            log.info("\nGetting person from elasticsearch\n")
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
