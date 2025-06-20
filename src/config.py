"""
Configuration management for FastUnstructAPI

This module handles all configuration and environment variable loading for the application.
"""

from typing import Optional
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Application configuration settings"""
    
    # AWS S3 Configuration
    aws_s3_key: str = Field(..., env="AWS_S3_KEY")
    aws_s3_secret: str = Field(..., env="AWS_S3_SECRET")
    
    # Unstructured.io Configuration
    unstruct_api_key: str = Field(..., env="UNSTRUCT_API_KEY")
    
    # Supabase Configuration
    supabase_password: str = Field(..., env="SUPABASE_PASSWORD")
    supabase_host: str = "aws-0-ap-southeast-2.pooler.supabase.com"
    supabase_port: str = "6543"
    supabase_username: str = "postgres.nwwqkubrlvmrycubylso"
    supabase_database: str = "postgres"
    
    # Application Configuration
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_config() -> Config:
    """Get the application configuration"""
    return Config()


def get_aws_config() -> dict:
    """Get AWS configuration dictionary"""
    config = get_config()
    return {
        "key": config.aws_s3_key,
        "secret": config.aws_s3_secret
    }


def get_supabase_config() -> dict:
    """Get Supabase configuration dictionary"""
    config = get_config()
    return {
        "host": config.supabase_host,
        "port": config.supabase_port,
        "username": config.supabase_username,
        "database": config.supabase_database,
        "password": config.supabase_password
    }


def get_unstructured_config() -> dict:
    """Get Unstructured.io configuration dictionary"""
    config = get_config()
    return {
        "api_key": config.unstruct_api_key,
        "endpoint": "https://api.unstructuredapp.io/general/v0/general"
    }
