"""
Configuration management - Simplified for Windows
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application Settings"""
    
    # API Settings
    APP_NAME: str = "PDF RAG API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # AI/ML Settings - Read from .env
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.1-8b-instant"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    
    # Embedding Settings (not used in minimal version)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Vector Database Settings
    CHROMA_PERSIST_DIR: str = "data/chroma"
    DEFAULT_SEARCH_K: int = 5
    MAX_SEARCH_K: int = 20
    
    # PDF Processing Settings
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "data/uploads"
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    # Chunk Settings
    CHUNK_SIZE_SMALL: int = 300
    CHUNK_SIZE_MEDIUM: int = 500
    CHUNK_SIZE_LARGE: int = 800
    CHUNK_OVERLAP_SMALL: int = 50
    CHUNK_OVERLAP_MEDIUM: int = 100
    CHUNK_OVERLAP_LARGE: int = 150
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "500 MB"
    LOG_RETENTION: str = "10 days"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()