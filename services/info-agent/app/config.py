import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings for info-agent"""

    ollama_base_url: str = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.2, alias="OLLAMA_TEMPERATURE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Redis Configuration
    redis_url: str = Field(default=None, alias="REDIS_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()

import logging
logging.basicConfig(level=settings.log_level)
