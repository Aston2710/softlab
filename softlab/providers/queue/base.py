from abc import ABC, abstractmethod
from typing import Any


class QueueProvider(ABC):

    @abstractmethod
    async def enqueue(self, task_name: str, payload: dict) -> str:
        """Encola una tarea. Retorna el job_id."""
        ...

    @abstractmethod
    async def get_status(self, job_id: str) -> dict:
        """Retorna el estado actual del job."""
        ...
