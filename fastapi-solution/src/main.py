import logging

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router
from core import config
from core.logger import LOGGING
from db import elastic, redis

# Конфигурация пиложения
app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    """Подключение к базам при старте сервера."""
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{config.ELASTIC_SCHEMA}{config.ELASTIC_HOST}:"
            f"{config.ELASTIC_PORT}"
        ]
    )


@app.on_event("shutdown")
async def shutdown():
    """Отключение от баз при выключении сервера."""
    await redis.redis.close()
    await elastic.es.close()


# Подключение роутера к серверу
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    """Основная точка входа сервиса api."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
