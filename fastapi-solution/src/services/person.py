from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film  # , FilmPerson
from models.person import Person
from services.abstracts import AbstractItemService
from services.es_queries import common, persons_in_films
from services.tools.person_films_dict import films_dict


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

            films_person = await self._get_person_films(person_id)

        except NotFoundError:
            return None
        person = Person(**doc["_source"], films=films_person)

        return person

    async def _get_person_films(self, person_id):
        index_ = "movies"
        # sort_field = "imdb_rating"
        # order = "desc"

        query_body = common.get_query()
        query_body["query"] = persons_in_films.get_query(person_id)

        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            films = [
                dict(Film(**doc["_source"])) for doc in docs["hits"]["hits"]
            ]
        except NotFoundError:
            return None

        films_person = films_dict(person_id, films)

        log.debug("\nfilms_person: \n%s\n", films_person)

        return films_person


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
