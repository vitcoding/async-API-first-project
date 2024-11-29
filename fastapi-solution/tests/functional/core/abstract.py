from abc import ABC, abstractmethod
from typing import Any


class SearchClient(ABC):
    @abstractmethod
    async def index_exists(self, index: str) -> bool:
        """Check if an index exists in the search system."""
        pass

    @abstractmethod
    async def delete_index(self, index: str) -> None:
        """Delete an existing index from the search system."""
        pass

    @abstractmethod
    async def create_index(self, index: str, settings: dict) -> None:
        """Create a new index in the search system."""
        pass

    @abstractmethod
    async def bulk_write(self, actions: list[dict]) -> tuple[int, bool]:
        """Perform bulk write operations on the search system."""
        pass

    @abstractmethod
    async def count_documents(self, index: str) -> int:
        """Count the number of documents in a given index."""
        pass


class CacheClient(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get a value from the cache by key."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the cache connection."""
        pass
