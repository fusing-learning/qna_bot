import pytest
from src.core.config import Settings, get_settings

def test_settings_initialization():
    """Test that settings are properly initialized with default values."""
    settings = Settings()
    assert settings.OPENAI_MODEL_NAME == "gpt-4.1-nano"
    assert settings.APP_ENV == "development"
    assert settings.DEBUG is True
    assert settings.CHROMA_PERSIST_DIRECTORY == "./data/chroma"
    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 8000

def test_openai_config():
    """Test OpenAI configuration settings."""
    settings = Settings()
    assert settings.OPENAI_API_KEY is not None
    assert settings.OPENAI_API_KEY != "your-api-key-here"

def test_app_settings():
    """Test application settings."""
    settings = Settings()
    assert settings.APP_ENV in ["development", "production", "testing"]
    assert isinstance(settings.DEBUG, bool)

def test_vector_store_config():
    """Test vector store configuration."""
    settings = Settings()
    assert settings.CHROMA_PERSIST_DIRECTORY == "./data/chroma"

def test_api_settings():
    """Test API configuration."""
    settings = Settings()
    assert settings.API_HOST == "0.0.0.0"
    assert isinstance(settings.API_PORT, int)
    assert 1024 <= settings.API_PORT <= 65535

def test_settings_caching():
    """Test that settings are properly cached."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Should be the same instance 