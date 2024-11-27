from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "GPU-Text-Service"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:70b"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    MAX_CONTEXT_LENGTH: int = 131072
    MODEL_EMBEDDING_SIZE: int = 8192
    
    # Model specific settings
    MODEL_BLOCK_COUNT: int = 80
    MODEL_ATTENTION_HEAD_COUNT: int = 64
    MODEL_ATTENTION_HEAD_COUNT_KV: int = 8
    MODEL_FEED_FORWARD_LENGTH: int = 28672
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8001"]
    
    class Config:
        env_file = ".env"

settings = Settings()
