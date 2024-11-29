from typing import Any

from redis.asyncio import Redis

from core.abstract import CacheClient


class RedisCacheClient(CacheClient):
    def __init__(self, host: str, port: int):
        self._client = Redis(host=host, port=port)

    async def get(self, key: str) -> Any:
        """Retrieve a value from the cache using the provided key."""
        return await self._client.get(key)

    async def close(self) -> None:
        """Close the Redis connection and release resources."""
        await self._client.aclose()
