from asyncio import sleep
from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from redis.asyncio import Redis

from core.config import log
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


# class Paginator:
#     def __init__(self, limit: int = 50, page: int = 1):
#         self.limit = limit
#         self.page = page

#     def __call__(self, limit: int):
#         if limit < self.limit:
#             return [{"limit": self.limit, "page": self.page}]
#         else:
#             return [{"limit": limit, "page": self.page}]


# def serialize_object(object: Optional[Film]) -> bytes:
#     return object.json().encode("utf-8")


# def deserialize_data(data: bytes) -> Optional[Film]:
#     deserialized = data.decode("utf-8")
#     return Film.parse_raw(deserialized)


class FilmListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def films_count_total(self):
        index_ = await self.elastic.count(
            index="movies",
        )
        count_total = int(index_["count"])
        return count_total

    async def get_film_list(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film]:

        log.info("\nЗапрос фильмов\n")

        # ###
        # for i in range(21):
        #     key = f"{sort_field}, {page_size}, {i}, {genre_uuid}"
        #     await self.redis.delete(key)
        # ###

        key = f"{sort_field}, {page_size}, {page_number}, {genre_uuid}"
        films = await self._films_from_cache(key)
        if not films:
            films = await self._get_films_from_elastic(
                sort_field, page_size, page_number, genre_uuid
            )
            if not films:
                return None
            await self._put_films_to_cache(key, films)

        return films

    async def _get_films_from_elastic(
        self,
        sort_field: str | None,
        page_size: int,
        page_number: int,
        genre_uuid: str | None,
    ) -> list[Film]:

        docs_total = await self.films_count_total()
        pages_total_float = docs_total / page_size
        pages_total = int(pages_total_float)
        if pages_total < pages_total_float:
            pages_total += 1

        if page_number < 1 or page_number > pages_total:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="page not found"
            )

        if page_number == pages_total:
            page_size_last = docs_total - (page_size * (pages_total - 1))

        order = ("asc", "desc")[sort_field.startswith("-")]
        if order == "desc":
            sort_field = sort_field[1:]

        query_body = {
            "size": (
                page_size_last if page_number == pages_total else page_size
            ),
            "from": (page_number - 1) * page_size,
            "sort": [
                {
                    sort_field: {"order": order, "missing": "_last"},
                }
            ],
        }

        # Надо будет скорректировать после добавления индексов по жанрам
        if genre_uuid is not None:
            query_body["query"] = {"match": {"genres": "Drama"}}

        log.info("\nquery_body: \n%s\n", query_body)

        try:
            log.info("\nGeting films from elasticsearch\n")
            docs = await self.elastic.search(
                index="movies",
                body=query_body,
            )
            films = [Film(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return films

    async def _films_from_cache(
        self,
        key: str,
    ) -> list[Film]:
        data = await self.redis.lrange(key, 0, -1)
        if not data:
            return None

        films = [Film.parse_raw(row) for row in data]

        return films

    async def _put_films_to_cache(
        self,
        key: str,
        films: list[Film],
    ) -> None:
        await self.redis.delete(key)
        for film in films:
            await self.redis.rpush(
                key,
                film.json(),
            )
        while True:
            try:
                await self.redis.setex(
                    key,
                    FILM_CACHE_EXPIRE_IN_SECONDS,
                )
            except TypeError as err:
                log.info(
                    "\nError '%s': \n%s\n",
                    type(err),
                    err,
                )
            if bool(await self.redis.exists(key)):
                log.info("\nAn array key has been created\n")
                break
            await sleep(0.1)


@lru_cache()
def get_film_list_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmListService:
    return FilmListService(redis, elastic)
