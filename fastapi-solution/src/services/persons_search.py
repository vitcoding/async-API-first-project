from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person, PersonBase
from services.abstracts import AbstractListService


class PersonListSearchService(AbstractListService):

    async def get_list(
        self,
        query: str | None,
        # sort_field: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Film]]:

        log.info("\nGetting persons.\n")

        key = f"{query}, {page_size}, {page_number}"
        # key = f"{query}, {sort_field}, {page_size}, {page_number}"
        persons = await self._get_from_cache(key, "person", is_list=True)
        if not persons:
            persons = await self._get_list_from_elastic(
                query, page_size, page_number
            )
            # persons = await self._get_list_from_elastic(
            #     query, sort_field, page_size, page_number
            # )

            if not persons:
                return None

            await self._put_to_cache(key, persons, "person")

        return persons

    async def _get_list_from_elastic(
        self,
        query: str | None,
        # sort_field: str | None,
        page_size: int,
        page_number: int,
    ) -> Optional[list[Person]]:

        index_ = "persons"
        docs_total = await self._docs_total(index_)
        pages_total = await self._pages_total(docs_total, page_size)
        page_size = await self._validate_pages(
            docs_total, page_number, pages_total, page_size
        )

        # order = ("asc", "desc")[sort_field.startswith("-")]
        # if order == "desc":
        #     sort_field = sort_field[1:]

        query_body = {
            "size": (page_size),
            "from": (page_number - 1) * page_size,
            # "sort": [
            #     {
            #         sort_field: {"order": order, "missing": "_last"},
            #     }
            # ],
        }

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
            docs = await self.elastic.search(
                index=index_,
                body=query_body,
            )
            persons = [
                PersonBase(**doc["_source"]) for doc in docs["hits"]["hits"]
            ]

            # print(persons)
            for pers in persons:
                print(dict(pers)["id"])

        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return persons


@lru_cache()
def get_person_list_search_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonListSearchService:
    return PersonListSearchService(redis, elastic)
