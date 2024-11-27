from typing import Any, List, Dict

from elasticsearch import AsyncElasticsearch, NotFoundError

from core.logger import log


class ElasticsearchService:
    """Сервис для работы с Elasticsearch."""

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search(self, index: str, body: dict) -> List[Dict[str, Any]]:
        """Поиск в Elasticsearch."""
        try:
            log.info("\nGetting data from Elasticsearch.\n")
            docs = await self.elastic.search(index=index, body=body)
            return docs["hits"]["hits"]
        except NotFoundError:
            return None

    async def count(self, index: str) -> int:
        """Получение количества документов в индексе."""
        data = await self.elastic.count(index=index)
        return int(data["count"])

    async def get(self, index: str, id) -> Dict[str, Any]:
        return await self.elastic.get(index=index, id=id)
