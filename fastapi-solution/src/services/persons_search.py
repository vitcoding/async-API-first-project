from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.logger import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person, PersonBase
from services.abstracts import AbstractListService, PersonFilmsMixin
from services.cache_service import CacheService
from services.elasticsearch_service import ElasticsearchService
from services.es_queries import common
from services.tools.person_films_dict import films_dict


class PersonListSearchService(AbstractListService, PersonFilmsMixin):
    """Класс для полнотекстового поиска персон."""

    async def get_list(
            self,
            query: str | None,
            page_size: int,
            page_number: int,
    ) -> list[Film] | None:
        """Основной метод получения списка персон."""

        log.info("\nGetting persons.\n")

        key = f"PersonSearch: {query}, size: {page_size}, page: {page_number}"
        persons = await self.get_from_cache(key, "person", is_list=True)
        if not persons:
            persons = await self._get_list_from_elastic(
                query, page_size, page_number
            )

            if not persons:
                return None

            await self.put_to_cache(key, persons, "person")

        return persons

    async def _get_list_from_elastic(
            self,
            query: str | None,
            page_size: int,
            page_number: int,
    ) -> list[Person] | None:
        """Метод получения списка персон из elasticsearch."""

        index_ = "persons"
        docs_total = await self.es_service.count(index_)
        pages_total = await self.get_pages_total(docs_total, page_size)
        page_size = await self.validate_pages(docs_total, page_number, pages_total, page_size)

        query_body = common.get_query(page_size, page_number, None)

        if query is not None:
            query_body["query"] = {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "full_name",
                    ],
                }
            }

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nSearching persons from elasticsearch\n")
            docs = await self.es_service.search(
                index=index_,
                body=query_body,
            )
            persons_query = [
                PersonBase(**doc["_source"]) for doc in docs
            ]

            persons = []
            for person in persons_query:
                person_id = dict(person)["id"]
                films = [
                    dict(film)
                    for film in await self._get_person_films(person_id)
                ]
                films_person = films_dict(person_id, films)
                person_temp = Person(
                    **dict(person),
                    films=films_person,
                )
                persons.append(person_temp)

        except NotFoundError:
            return None

        log.debug("\ndocs: \n%s\n", docs)

        return persons


@lru_cache()
def get_person_list_search_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonListSearchService:
    """PersonListSearchService."""
    cache_service = CacheService(redis)
    es_service = ElasticsearchService(elastic)
    return PersonListSearchService(cache_service, es_service)
