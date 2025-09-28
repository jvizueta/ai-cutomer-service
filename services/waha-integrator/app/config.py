import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """WAHA Integrator settings"""
    
    # Service URLs
    waha_base_url: str = Field(default="http://waha.waha-infra.svc.cluster.local:3000", alias="WAHA_BASE_URL")
    lyra_base_url: str = Field(default="http://lyra.lyra-ns.svc.cluster.local:8000", alias="LYRA_BASE_URL")
    
    # WAHA API Configuration
    waha_api_key: Optional[str] = Field(default=None, alias="WAHA_API_KEY")
    
    # Message Processing
    default_language: str = Field(default="English", alias="DEFAULT_LANGUAGE")
    response_timeout: int = 30
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    
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