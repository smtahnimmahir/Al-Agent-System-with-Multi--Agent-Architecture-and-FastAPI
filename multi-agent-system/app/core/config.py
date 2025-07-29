import os
from typing import Optional
from pydantic_settings import BaseSettings  # Changed from pydantic to pydantic_settings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings for environment validation"""
    
    # API Keys
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")
    
    # Application Settings
    app_name: str = Field(default="Multi-Agent System", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Model Configuration
    llm_model: str = Field(default="llama3-70b-8192", alias="LLM_MODEL")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    
    # Agent Configuration
    agent_timeout: int = Field(default=30, alias="AGENT_TIMEOUT")
    max_search_results: int = Field(default=5, alias="MAX_SEARCH_RESULTS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()