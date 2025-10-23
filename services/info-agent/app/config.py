import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings for info-agent"""

    ollama_base_url: str = Field(default="http://ollama:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1", alias="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.2, alias="OLLAMA_TEMPERATURE")
    ollama_timeout: int = Field(default=60, alias="OLLAMA_TIMEOUT")
    system_prompt: str = Field(default="", alias="SYSTEM_PROMPT")
    default_language: str = Field(default="english", alias="DEFAULT_LANGUAGE")
    recent_messages_window: int = Field(default=6, alias="RECENT_MESSAGES_WINDOW")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    host: str = "0.0.0.0"
    port: int = 8000
    message_summary_char_limit: int = Field(default=600, alias="MESSAGE_SUMMARY_CHAR_LIMIT")
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
