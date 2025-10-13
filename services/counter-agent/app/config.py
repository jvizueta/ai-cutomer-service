# services/counter-agent/app/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    
    
    # Model Configuration
    lc_model: str = Field(default="gpt-4o-mini", alias="LC_MODEL")
    lc_temperature: float = Field(default=0.2, alias="LC_TEMPERATURE")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Redis Configuration
    redis_url: str = Field(default=None, alias="REDIS_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Configure logging
import logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)