"""
Configuration management for FastUnstructAPI

This module handles all configuration and environment variable loading for the application.
"""

import logging
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, HttpUrl, ValidationError

# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Application configuration settings"""
    
    def __init__(self, **data):
        super().__init__(**data)
        logger.debug("Initializing Config with environment variables:")
        for field_name, field in self.__fields__.items():
            env_vars = getattr(field.field_info, 'env_names', [])
            env_value = None
            for env_var in env_vars:
                if env_value is None:
                    env_value = os.getenv(env_var)
            logger.debug(f"  {field_name}: {'***' if 'password' in field_name or 'key' in field_name else env_value} (from env: {env_vars})")
    
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
    try:
        # Log environment variables (safely, without sensitive data)
        env_vars = {
            'AWS_ACCESS_KEY_ID': '***' if os.getenv('AWS_ACCESS_KEY_ID') else None,
            'AWS_SECRET_ACCESS_KEY': '***' if os.getenv('AWS_SECRET_ACCESS_KEY') else None,
            'UNSTRUCTURED_API_KEY': '***' if os.getenv('UNSTRUCTURED_API_KEY') else None,
            'SUPABASE_HOST': os.getenv('SUPABASE_HOST'),
            'SUPABASE_USERNAME': os.getenv('SUPABASE_USERNAME'),
            'SUPABASE_DATABASE': os.getenv('SUPABASE_DATABASE'),
            'SUPABASE_PASSWORD': '***' if os.getenv('SUPABASE_PASSWORD') else None,
        }
        logger.debug(f"Environment variables: {env_vars}")
        
        # Try to load config
        config = Config()
        logger.info("Successfully loaded configuration")
        logger.debug(f"Loaded config: {config}")
        return config
        
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


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
    try:
        logger.debug("Loading Supabase configuration...")
        config = get_config()
        
        # Log the actual values being used (safely)
        supabase_config = {
            "host": config.supabase_host,
            "port": config.supabase_port,
            "username": config.supabase_username,
            "database": config.supabase_database,
            "password": "***" if config.supabase_password else None,
            "table_name": config.supabase_table
        }
        
        logger.debug(f"Supabase config loaded: { {k: '***' if 'password' in k else v for k, v in supabase_config.items()} }")
        
        # Verify required fields
        required_fields = ['host', 'username', 'database', 'password']
        missing_fields = [field for field in required_fields if not supabase_config.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required Supabase configuration: {', '.join(missing_fields)}")
            logger.error("Current Supabase config:")
            for k, v in supabase_config.items():
                logger.error(f"  {k}: {'***' if 'password' in k else v}")
        
        return supabase_config
        
    except Exception as e:
        logger.error(f"Error loading Supabase configuration: {str(e)}", exc_info=True)
        raise


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
