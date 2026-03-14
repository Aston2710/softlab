# ARCHIVO INMUTABLE — ver ADR-02
from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ) -> str:
        """Retorna el texto de la completación. Lanza LLMError en fallo."""
        ...

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema: dict,
        system: str = "",
    ) -> dict:
        """
        Retorna JSON validado contra schema.
        Reintenta hasta 2 veces si la respuesta no es JSON válido.
        Lanza LLMValidationError si no logra JSON válido tras los reintentos.
        """
        ...

    def health_check(self) -> bool:
        return True


class LLMError(Exception):
    pass


class LLMValidationError(LLMError):
    pass
