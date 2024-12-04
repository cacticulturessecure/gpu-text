from pydantic_settings import BaseSettings
from typing import List, Dict, Any
from functools import lru_cache
import os
import json

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
    MAX_TOKENS: int = 131072
    MAX_CONTEXT_LENGTH: int = 131072
    MODEL_EMBEDDING_SIZE: int = 8192
    
    # Model specific settings
    MODEL_BLOCK_COUNT: int = 80
    MODEL_ATTENTION_HEAD_COUNT: int = 64
    MODEL_ATTENTION_HEAD_COUNT_KV: int = 8
    MODEL_FEED_FORWARD_LENGTH: int = 28672
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "https://dev.cacticultures.com",
        "https://staging.cacticultures.com",
        "https://cacticultures.com",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
        "http://localhost:8005",
        "http://localhost:8006",
        "http://localhost:8007",
        "http://localhost:8008",
        "http://localhost:8009",
        "http://localhost:8010"
    ]

    # Available Models
    AVAILABLE_MODELS: List[str] = ["llama3.1:70b", "qwq:32b"]
    
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
        env_prefix = "CACTICULTURES_"
        
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

    def parse_env_var(self, field_name: str, raw_val: str) -> Any:
        """
        Custom parser for environment variables
        """
        if field_name in ["ALLOWED_ORIGINS", "AVAILABLE_MODELS"] and isinstance(raw_val, str):
            try:
                return json.loads(raw_val)
            except json.JSONDecodeError:
                # Fall back to comma-separated string for backward compatibility
                return [x.strip() for x in raw_val.split(",")]
        return raw_val

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()

# Create settings instance
settings = get_settings()
