from pydantic_settings import BaseSettings
from typing import List, Dict, Any
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Basic API Settings
    APP_NAME: str = "GPU-Text-Service"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Ollama Settings
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
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "https://dev.cacticultures.com",
        "https://staging.cacticultures.com",
        "https://cacticultures.com",
        "http://localhost:8001",  # Dev server
        "http://localhost:8002",  # Staging server
        "http://localhost:8003",  # Prod server
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8000"   # Local development
    ]

    # Security Settings
    API_KEY_HEADER: str = "X-API-Key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECURITY_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model Response Configuration
    RESPONSE_CONFIG: Dict[str, Any] = {
        "max_new_tokens": MAX_TOKENS,
        "temperature": DEFAULT_TEMPERATURE,
        "top_p": 0.9,
        "top_k": 50,
        "repeat_penalty": 1.1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    class Config:
        env_file = ".env"
        case_sensitive = True
        
        # Environment variable schema
        env_prefix = "CACTICULTURES_"  # Use this prefix for environment variables
        
        # Additional environment files for different environments
        env_file_encoding = 'utf-8'
        extra = "allow"  # Allow extra fields in the settings

    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins based on environment
        """
        if self.ENVIRONMENT == "production":
            return [origin for origin in self.ALLOWED_ORIGINS 
                   if not origin.startswith("http://localhost")]
        return self.ALLOWED_ORIGINS

    def get_redis_url(self) -> str:
        """
        Get Redis URL from configuration
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_model_config(self) -> Dict[str, Any]:
        """
        Get complete model configuration
        """
        return {
            "model": self.OLLAMA_MODEL,
            "embedding_size": self.MODEL_EMBEDDING_SIZE,
            "block_count": self.MODEL_BLOCK_COUNT,
            "attention_head_count": self.MODEL_ATTENTION_HEAD_COUNT,
            "attention_head_count_kv": self.MODEL_ATTENTION_HEAD_COUNT_KV,
            "feed_forward_length": self.MODEL_FEED_FORWARD_LENGTH,
        }

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()

# Create settings instance
settings = get_settings()
