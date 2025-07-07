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
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'DEBUG'))
logger = logging.getLogger(__name__)


class Config(BaseSettings):
    """Application configuration settings"""
    
    def __init__(self, **data):
        # First log all environment variables (for debugging)
        logger.debug("Available environment variables:")
        for k, v in os.environ.items():
            if any(skip in k.lower() for skip in ['key', 'pass', 'token', 'secret']):
                logger.debug(f"  {k} = ***REDACTED***")
            else:
                logger.debug(f"  {k} = {v}")
                
        # Then initialize the config
        super().__init__(**data)
        
        # Log the loaded configuration
        logger.debug("\nLoaded configuration:")
        for field_name, field in self.__fields__.items():
            env_vars = getattr(field.field_info, 'env_names', [])
            field_value = getattr(self, field_name, None)
            
            # Log the field and its source
            source = "default"
            for env_var in env_vars:
                if os.getenv(env_var) is not None:
                    source = f"env:{env_var}"
                    break
                    
            # Redact sensitive information
            display_value = field_value
            if field_value and any(skip in field_name.lower() for skip in ['key', 'pass', 'token', 'secret']):
                display_value = '***REDACTED***'
                
            logger.debug(f"  {field_name}: {display_value} (from {source})")
            
            # Log warning if required field is missing
            if field.is_required() and field_value is None:
                logger.warning(f"⚠️  Required field '{field_name}' is None")
    
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
    """Get Supabase configuration dictionary with validation.
    
    Returns:
        Dict containing Supabase connection details
        
    Raises:
        ValueError: If required configuration is missing
    """
    try:
        logger.info("🔍 Loading Supabase configuration...")
        config = get_config()
        
        # Build config dictionary with validation
        supabase_config = {
            "host": config.supabase_host,
            "port": config.supabase_port,
            "username": config.supabase_username,
            "database": config.supabase_database,
            "password": config.supabase_password,
            "table_name": config.supabase_table
        }
        
        # Log the config (safely)
        safe_config = {k: '***' if k == 'password' else v 
                      for k, v in supabase_config.items()}
        logger.debug(f"Supabase configuration: {safe_config}")
        
        # Validate required fields
        required_fields = {
            'host': "Supabase host (SUPABASE_HOST)",
            'username': "Database username (SUPABASE_USERNAME)",
            'database': "Database name (SUPABASE_DATABASE)",
            'password': "Database password (SUPABASE_PASSWORD)"
        }
        
        missing = [desc for field, desc in required_fields.items() 
                  if not supabase_config.get(field)]
        
        if missing:
            error_msg = f"Missing required Supabase configuration: {', '.join(missing)}"
            logger.error(error_msg)
            
            # Log current environment for debugging
            logger.debug("Current environment variables:")
            for k, v in os.environ.items():
                if k.startswith('SUPABASE_') or k.startswith('AWS_'):
                    logger.debug(f"  {k} = {'***' if any(x in k.lower() for x in ['key', 'pass', 'secret']) else v}")
            
            raise ValueError(error_msg)
            
        logger.info("✅ Successfully loaded Supabase configuration")
        return supabase_config
        
    except Exception as e:
        logger.error("❌ Failed to load Supabase configuration")
        logger.exception("Configuration error:")
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
