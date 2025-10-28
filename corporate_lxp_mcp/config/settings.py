"""Application settings following SOLID principles"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_title: str = Field(default="Corporate LXP API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=9001, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Registry Configuration
    registry_host: str = Field(default="0.0.0.0", description="Registry host")
    registry_port: int = Field(default=9000, description="Registry port")
    
    # MCP Configuration
    mcp_server_name: str = Field(default="corporate-lxp-mcp", description="MCP server name")
    mcp_server_version: str = Field(default="1.0.0", description="MCP server version")
    
    # Database Configuration (for future use)
    database_url: Optional[str] = Field(default=None, description="Database URL")
    
    # Redis Configuration (for registry)
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log level")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_prefix = "CORPORATE_LXP_"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
