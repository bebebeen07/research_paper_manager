"""
Configuration Management

This module handles all configuration and environment variables.
It reads from the .env file and provides defaults.

Key Concepts:
- Pydantic Settings: Validates and loads environment variables
- Type hints: mypy can catch config errors early
- Defaults: Provides sensible defaults for development
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Example .env file:
        DATABASE_URL=sqlite:///./data/papers.db
        CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxx
        DEBUG=True
    """
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/papers.db"
    
    # API Keys
    CLAUDE_API_KEY: str = ""  # Will error if not set in production
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf"]
    
    # Debug mode
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
