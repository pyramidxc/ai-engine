"""
Configuration management for the Attack Path Engine.

Centralizes all environment variables and application settings.

Environment Variables:
    - OPENAI_API_KEY: LLM API key (for OpenAI-compatible servers)
    - OPENAI_API_BASE: LLM server base URL (default: OpenAI API)
    - LLM_MODEL: Model identifier (loaded from .env)
    - LLM_TEMPERATURE: Creativity level 0.0-2.0 (default: 0.2)

Usage:
    >>> from app.config import settings
    >>> print(settings.LLM_MODEL)
    
Notes:
    - Settings loaded once at startup from .env file
    - Supports OpenAI-compatible servers (OpenAI, LMStudio, Ollama, etc.)
"""
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    
    All configuration comes from .env file to support different models
    and deployment environments without code changes.
    """
    
    # API Configuration
    API_TITLE: str = "Attack Path Engine"
    API_VERSION: str = "1.0.0"
    
    # LLM Configuration
    # Model identifier - supports any OpenAI-compatible server
    # Examples: "openai/gpt-4o", "openai/deepseek-r1-0528-qwen3-8b"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")
    
    # Temperature for LLM responses
    # 0.2 = Optimized for consistency (recommended for attack paths)
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    
    # API Key (required for OpenAI-compatible servers)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    @classmethod
    def validate(cls):
        """
        Validate required configuration.
        
        Raises:
            ValueError: If required settings are missing
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Set it in your .env file."
            )
        if not cls.LLM_MODEL:
            raise ValueError(
                "LLM_MODEL environment variable is required. "
                "Set it in your .env file."
            )


# Global settings instance
settings = Settings()
