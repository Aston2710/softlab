from softlab.config import settings
from softlab.providers.llm.base import LLMProvider
from softlab.providers.queue.base import QueueProvider
from softlab.providers.storage.base import StorageProvider


def get_llm_provider() -> LLMProvider:
    match settings.llm_provider:
        case "groq":
            from softlab.providers.llm.groq_provider import GroqProvider
            return GroqProvider()
        case "ollama":
            from softlab.providers.llm.ollama_provider import OllamaProvider
            return OllamaProvider()
        case "claude":
            from softlab.providers.llm.claude_provider import ClaudeProvider
            return ClaudeProvider()
        case _:
            raise ValueError(f"LLM provider desconocido: {settings.llm_provider}")


def get_queue_provider() -> QueueProvider:
    match settings.queue_provider:
        case "valkey":
            from softlab.providers.queue.valkey_provider import ValkeyProvider
            return ValkeyProvider()
        case _:
            raise ValueError(f"Queue provider desconocido: {settings.queue_provider}")


def get_storage_provider() -> StorageProvider:
    match settings.storage_provider:
        case "minio":
            from softlab.providers.storage.minio_provider import MinioProvider
            return MinioProvider()
        case _:
            raise ValueError(f"Storage provider desconocido: {settings.storage_provider}")
