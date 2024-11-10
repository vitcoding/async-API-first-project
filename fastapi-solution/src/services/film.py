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


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def films_count_total(self):
        index_ = await self.elastic.count(
            index="movies",
        )
        count_total = int(index_["count"])
        return count_total

    # Надо будет добавить кэширование
    async def get_film_list(
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

        if sort_field.startswith("-"):
            sort_field = sort_field[1:]
            order = "desc"
        else:
            order = "asc"

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
            docs = await self.elastic.search(
                index="movies",
                body=query_body,
            )
            films = [Film(**doc["_source"]) for doc in docs["hits"]["hits"]]
        except NotFoundError:
            return None
        log.debug("\ndocs: \n%s\n", docs["hits"]["hits"])
        return films

    async def get_by_id(self, film_id: str) -> Optional[Film]:

        log.info("\nЗапрос фильма по id '%s'\n", film_id)

        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            log.info("\nПолучение данных из ElasticSearch\n")
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
