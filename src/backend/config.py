"""
Configuration management using pydantic-settings.

All configuration values can be overridden via environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Load .env from project root
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    deepseek_api_key: str = "your_key_here"  # Default for testing, override in .env
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_timeout: int = 60
    deepseek_model: str = "deepseek-chat"

    # Content Detection Configuration
    min_content_page: int = 10
    char_jump_threshold: float = 3.0

    # Semantic Similarity Configuration
    similarity_threshold: float = 0.90
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # RAG Configuration
    rag_top_k: int = 3
    rag_max_tokens: int = 1000
    rag_temperature: float = 0.3

    # Knowledge Graph Configuration
    kg_max_chunks: int = 50
    kg_max_tokens: int = 2000
    kg_temperature: float = 0.3

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Frontend Configuration
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Diagnostic logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"[CONFIG] Settings loaded - API key present: {bool(settings.deepseek_api_key and settings.deepseek_api_key != 'your_key_here')}")
logger.info(f"[CONFIG] API key value: {settings.deepseek_api_key[:10]}..." if settings.deepseek_api_key and settings.deepseek_api_key != 'your_key_here' else "[CONFIG] API key NOT configured")
