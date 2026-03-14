from abc import ABC, abstractmethod


class StorageProvider(ABC):

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Sube un objeto. Retorna la URL o key de acceso."""
        ...

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Descarga un objeto por key."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Elimina un objeto."""
        ...
