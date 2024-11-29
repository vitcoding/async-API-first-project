from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from core.abstract import SearchClient


class ElasticsearchClient(SearchClient):
    def __init__(self, hosts: list[str], verify_certs: bool = True):
        self._client = AsyncElasticsearch(
            hosts=hosts, verify_certs=verify_certs
        )

    async def index_exists(self, index: str) -> bool:
        """Check if an index exists in Elasticsearch."""
        return await self._client.indices.exists(index=index)

    async def delete_index(self, index: str) -> None:
        """Delete an index in Elasticsearch."""
        await self._client.indices.delete(index=index)

    async def create_index(self, index: str, settings) -> None:
        """Create an index in Elasticsearch."""
        await self._client.indices.create(index=index, **settings)

    async def bulk_write(
        self, actions: list[dict], refresh="wait_for"
    ) -> tuple[int, bool]:
        """Bulk write actions in Elasticsearch."""
        return await async_bulk(
            client=self._client, actions=actions, refresh=refresh
        )

    async def count_documents(self, index: str) -> int:
        """Count documents in Elasticsearch."""
        response = await self._client.count(index=index)
        return response["count"]

    async def close(self) -> None:
        """Close Elasticsearch."""
        await self._client.close()
