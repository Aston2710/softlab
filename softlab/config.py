from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Providers
    llm_provider: str = "groq"
    queue_provider: str = "valkey"
    storage_provider: str = "minio"

    # LLM
    groq_api_key: str = ""
    claude_api_key: str = ""
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Base de datos
    database_url: str = "postgresql+asyncpg://softlab:softlab@localhost:5432/softlab"

    # Valkey
    valkey_url: str = "redis://localhost:6379/0"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "softlab-artifacts"

    # Análisis
    sandbox_timeout: int = 300
    max_project_size_mb: int = 500
    rag_max_tokens: int = 6000
    rag_confidence_threshold: float = 0.70

    # Pesos de scoring (deben sumar 1.0)
    weight_security: float = 0.25
    weight_static: float = 0.20
    weight_architecture: float = 0.20
    weight_testing: float = 0.20
    weight_performance: float = 0.15

    # API
    secret_key: str = "dev-secret-key-cambiar-en-produccion"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Frontend
    next_public_api_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
