from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router
from core.config import settings
from db import elastic, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к базам при старте сервера
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}{settings.elastic_host}:"
            f"{settings.elastic_port}"
        ]
    )
    yield
    # Отключение от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Конфигурация приложения
app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

# Подключение роутера к серверу
app.include_router(router, prefix="/api")
