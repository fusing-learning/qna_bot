from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL_NAME: str = "gpt-4.1-nano"
    
    # Application Configuration
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/vector_store"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = '.env'
        case_sensitive = True

    def validate_api_key(self) -> bool:
        """Validate that the OpenAI API key is set and not empty."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != 'your-api-key-here')

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    """
    return Settings()

# Create global settings instance
settings = get_settings()

# Export settings
__all__ = ['settings'] 