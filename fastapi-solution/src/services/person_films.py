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


class PersonFilmListService(AbstractItemService):

    async def get_by_id(self, person_id: str) -> Optional[Person]:

        log.info("\nGetting person '%s'.\n", person_id)

        person_films = await self._get_from_cache(
            str(person_id) + "_films", "film"
        )
        if not person_films:
            person_films = await self._get_item_from_elastic(person_id)

            # # print(person)
            # print(type(person))
            # for p in person:
            #     print(p)

            if not person_films:
                return None

            await self._put_to_cache(
                str(person_id) + "_films", person_films, "film"
            )

        return person_films

    async def _get_item_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            log.info("\nGetting person from elasticsearch\n")
            doc = await self.elastic.get(index="persons", id=person_id)

            films_person = await self._get_person_films(person_id)

        except NotFoundError:
            return None
        # person_films = [Film(**film) for film in films_person]

        return films_person
        # return person_films

    async def _get_person_films(self, person_id):
        index_ = "movies"
        sort_field = "imdb_rating"
        order = "desc"

        query_body = {
            # "size": (page_size),
            # "from": (page_number - 1) * page_size,
            "sort": [
                {
                    sort_field: {"order": order, "missing": "_last"},
                }
            ],
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
            },
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

        log.debug("\nfilms_person: \n%s\n", films)

        return films


@lru_cache()
def get_person_film_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonFilmListService:
    return PersonFilmListService(redis, elastic)
