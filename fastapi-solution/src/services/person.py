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


class PersonService(AbstractItemService):

    async def get_by_id(self, person_id: str) -> Optional[Person]:

        log.info("\nGetting person '%s'.\n", person_id)

        person = await self._get_from_cache(str(person_id), "person")
        if not person:
            person = await self._get_item_from_elastic(person_id)

            # # print(person)
            # print(type(person))
            # for p in person:
            #     print(p)

            if not person:
                return None
            await self._put_to_cache(str(person_id), person, "person")

        return person

    async def _get_item_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            log.info("\nGetting person from elasticsearch\n")
            doc = await self.elastic.get(index="persons", id=person_id)

            films_person = await self._get_person_films(person_id)

            # print(films_person)
            # for f in films_person:
            #     print(f)
            #     print()

        except NotFoundError:
            return None
        person = Person(**doc["_source"], films=films_person)

        print(person)

        return person

    async def _get_person_films(self, person_id):
        index_ = "movies"
        sort_field = "imdb_rating"
        order = "desc"

        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": person_id}},
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.id": person_id}},
                            }
                        },
                    ]
                }
            }
        }

        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            films = [Film(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None

        films_person = []
        for film in films:
            film_temp, roles_temp = {}, []
            for key, value in dict(film).items():
                match key:
                    case "id":
                        film_temp[key] = value
                    case "directors" | "actors" | "writers":
                        for item in value:
                            if item["id"] == person_id:
                                roles_temp.append(key[:-1])
            film_temp["roles"] = sorted(roles_temp)

            films_person.append(film_temp)
            # films_person.append(FilmPerson(**film_temp))

            print(films_person)
            print()

        return films_person


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
