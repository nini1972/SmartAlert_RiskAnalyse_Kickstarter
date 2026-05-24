"""Configuration settings for the application."""

import os
import tempfile
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # MongoDB configuration
    MONGO_URL: str = Field(..., env="MONGO_URL")
    DB_NAME: str = Field(..., env="DB_NAME")
    
    # OpenAI configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    
    # API configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Kickstarter Investment Tracker"
    
    # CORS origins
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://d2b4b685-66a1-4946-9970-01e9da7727d3.preview.emergentagent.com",
        env="BACKEND_CORS_ORIGINS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # Scraping configuration
    SCRAPE_TIMEOUT_SECONDS: int = Field(default=15, env="SCRAPE_TIMEOUT_SECONDS")
    SCRAPE_MAX_RETRIES: int = Field(default=3, env="SCRAPE_MAX_RETRIES")
    SCRAPE_CACHE_TTL_SECONDS: int = Field(default=600, env="SCRAPE_CACHE_TTL_SECONDS")
    
    # Cache directory for scraping
    SCRAPE_CACHE_DIR: str = Field(default_factory=lambda: os.path.join(tempfile.gettempdir(), "kickstarter_scrape_cache"))
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a global settings object
settings = Settings()
