"""
Configuration management for FastUnstructAPI

This module handles all configuration and environment variable loading for the application.
"""

from typing import Optional, Dict, Any
import os
from pydantic_settings import BaseSettings
from pydantic import Field, HttpUrl


class Config(BaseSettings):
    """Application configuration settings"""
    
    # AWS S3 Configuration
    aws_access_key_id: str = Field(..., env=["AWS_ACCESS_KEY_ID", "AWS_S3_KEY"])
    aws_secret_access_key: str = Field(..., env=["AWS_SECRET_ACCESS_KEY", "AWS_S3_SECRET"])
    aws_session_token: Optional[str] = Field(None, env="AWS_SESSION_TOKEN")
    aws_region: str = Field("ap-southeast-2", env="AWS_REGION")
    
    # Unstructured.io Configuration
    unstructured_api_key: str = Field(..., env=["UNSTRUCTURED_API_KEY", "UNSTRUCT_API_KEY"])
    unstructured_api_url: str = Field(
        "https://api.unstructured.io",
        env="UNSTRUCTURED_API_URL"
    )
    
    # Supabase Configuration
    supabase_host: str = Field(
        "aws-0-ap-southeast-2.pooler.supabase.com",
        env="SUPABASE_HOST"
    )
    supabase_port: int = Field(5432, env="SUPABASE_PORT")
    supabase_username: str = Field(
        "postgres.nwwqkubrlvmrycubylso",
        env="SUPABASE_USERNAME"
    )
    supabase_database: str = Field("postgres", env="SUPABASE_DATABASE")
    supabase_password: str = Field(..., env="SUPABASE_PASSWORD")
    supabase_table: str = Field("elements", env="SUPABASE_TABLE")
    
    # Application Configuration
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_config() -> Config:
    """Get the application configuration"""
    return Config()


def get_aws_config() -> Dict[str, Any]:
    """Get AWS configuration dictionary
    
    Returns:
        Dict containing AWS credentials and configuration
    """
    config = get_config()
    return {
        "key": config.aws_access_key_id,
        "secret": config.aws_secret_access_key,
        "token": config.aws_session_token,
        "region": config.aws_region
    }


def get_supabase_config() -> Dict[str, Any]:
    """Get Supabase configuration dictionary
    
    Returns:
        Dict containing Supabase connection details
    """
    config = get_config()
    return {
        "host": config.supabase_host,
        "port": config.supabase_port,
        "username": config.supabase_username,
        "database": config.supabase_database,
        "password": config.supabase_password,
        "table_name": config.supabase_table
    }


def get_unstructured_config() -> Dict[str, Any]:
    """Get Unstructured.io configuration dictionary
    
    Returns:
        Dict containing Unstructured API configuration
    """
    config = get_config()
    return {
        "api_key": config.unstructured_api_key,
        "endpoint": config.unstructured_api_url
    }
