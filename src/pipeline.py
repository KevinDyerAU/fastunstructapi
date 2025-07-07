"""
Document processing pipeline implementation

This module implements the document processing pipeline using the updated
Unstructured.io workflow client for ingestion, processing, and storage.
"""

from typing import List, Dict, Any, Optional, Union
import logging
import os
import json
from pathlib import Path

# Local implementation of workflow client
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class S3SourceConfig:
    """Configuration for S3 source connector."""
    bucket_uri: str
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    recursive: bool = True
    custom_url: Optional[str] = None

@dataclass
class SupabaseDestinationConfig:
    """Configuration for Supabase (PostgreSQL) destination connector."""
    host: str
    database_name: str
    username: str
    password: str
    port: int = 5432
    table_name: str = "elements"
    batch_size: int = 100

@dataclass
class WorkflowConfig:
    """Configuration for the document processing workflow."""
    name: str
    source_config: S3SourceConfig
    destination_config: SupabaseDestinationConfig
    schedule: Optional[Dict[str, Any]] = None
    reprocess_all: bool = False

class UnstructuredWorkflowClient:
    """Client for managing document processing workflows."""
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        self.api_key = api_key
        self.server_url = server_url or "https://api.unstructured.io"
        logger.info("Initialized UnstructuredWorkflowClient")
    
    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow."""
        logger.info("Creating workflow with config: %s", workflow_config)
        return {"id": "workflow_123", "status": "created"}
    
    def run_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Run an existing workflow."""
        logger.info("Running workflow: %s", workflow_id)
        return {"run_id": f"run_{workflow_id}", "status": "started"}

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Exception raised for pipeline processing errors"""
    pass


def get_metadata_includes() -> List[str]:
    """Get the list of metadata fields to include in processed data"""
    return [
        "id", "element_id", "text", "embeddings", "type", "system", "layout_width",
        "layout_height", "points", "url", "version", "date_created", "date_modified",
        "date_processed", "permissions_data", "record_locator", "category_depth",
        "parent_id", "attached_filename", "filetype", "last_modified", "file_directory",
        "filename", "languages", "page_number", "links", "page_name", "link_urls",
        "link_texts", "sent_from", "sent_to", "subject", "section", "header_footer_type",
        "emphasized_text_contents", "emphasized_text_tags", "text_as_html", "regex_metadata",
        "detection_class_prob"
    ]


def create_workflow_config(
    folder: str,
    aws_config: Dict[str, str],
    unstructured_config: Dict[str, str],
    supabase_config: Dict[str, str],
    strategy: str = "hi_res"
) -> WorkflowConfig:
    """Create and configure the document processing workflow

    Args:
        folder (str): S3 folder path to process (e.g., s3://bucket/path/)
        aws_config (Dict[str, str]): AWS configuration with 'key', 'secret', and optional 'token'
        unstructured_config (Dict[str, str]): Unstructured.io configuration with 'api_key' and 'endpoint'
        supabase_config (Dict[str, str]): Supabase configuration with 'host', 'port', 'username', 'password', 'database'
        strategy (str): Processing strategy to use (auto, fast, hi_res, ocr_only, vlm)

    Returns:
        WorkflowConfig: Configured workflow instance
    """
    try:
        # Extract bucket and prefix from folder path
        if not folder.startswith('s3://'):
            raise ValueError("Folder path must start with 's3://'")
            
        # Configure S3 source
        s3_config = S3SourceConfig(
            bucket_uri=folder,
            aws_access_key_id=aws_config.get('key'),
            aws_secret_access_key=aws_config.get('secret'),
            aws_session_token=aws_config.get('token'),
            recursive=True
        )
        
        # Configure Supabase destination
        supabase_config = SupabaseDestinationConfig(
            host=supabase_config['host'],
            database_name=supabase_config['database'],
            port=supabase_config.get('port', 5432),
            username=supabase_config['username'],
            password=supabase_config['password'],
            table_name="elements"
        )
        
        # Create workflow config
        workflow_config = WorkflowConfig(
            name=f"process_{Path(folder).name or 'root'}",
            source_config=s3_config,
            destination_config=supabase_config
        )
        
        return workflow_config
        
    except Exception as e:
        logger.error(f"Error creating workflow config: {str(e)}")
        raise PipelineError(f"Failed to create workflow configuration: {str(e)}")


def process_documents(
    folder: str,
    aws_config: Optional[Dict[str, str]] = None,
    unstructured_config: Optional[Dict[str, str]] = None,
    supabase_config: Optional[Dict[str, str]] = None,
    strategy: str = "hi_res"
) -> Dict[str, str]:
    """Process documents from S3 using the configured pipeline

    Args:
        folder (str): S3 folder path to process
        aws_config (Optional[Dict[str, str]]): AWS configuration
        unstructured_config (Optional[Dict[str, str]]): Unstructured.io configuration
        supabase_config (Optional[Dict[str, str]]): Supabase configuration
        strategy (str): Partitioning strategy to use (auto, fast, hi_res, ocr_only, vlm)

    Returns:
        Dict[str, str]: Processing result
    """
    try:
        # Get configurations from config module if not provided
        aws_config = aws_config or config.get_aws_config()
        unstructured_config = unstructured_config or config.get_unstructured_config()
        supabase_config = supabase_config or config.get_supabase_config()

        # Create and run the pipeline
        pipeline = create_workflow_config(
            folder=folder,
            aws_config=aws_config,
            unstructured_config=unstructured_config,
            supabase_config=supabase_config,
            strategy=strategy
        )
        pipeline.run()

        return {
            "message": "File processing completed",
            "folder": folder
        }
    except PipelineError as e:
        logger.error(f"Pipeline processing failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        raise PipelineError(f"Unexpected error: {str(e)}")


def process_single_file(
    s3_path: str,
    aws_config: Dict[str, str],
    unstructured_config: Dict[str, str],
    strategy: str = "hi_res"
) -> Dict[str, Any]:
    """Process a single file from S3 using Unstructured API

    Args:
        s3_path (str): S3 path to the file (e.g., s3://bucket/path/to/file.pdf)
        aws_config (Dict[str, str]): AWS configuration
        unstructured_config (Dict[str, str]): Unstructured.io configuration
        strategy (str): Partitioning strategy to use (auto, fast, hi_res, ocr_only, vlm)

    Returns:
        Dict[str, Any]: Processing result containing elements and metadata
    """
    try:
        # Extract bucket and key from S3 path
        if not s3_path.startswith("s3://"):
            raise ValueError("S3 path must start with 's3://' format")
            
        bucket_key = s3_path[5:]  # Remove "s3://"
        bucket, key = bucket_key.split("/", 1)

        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_config["key"],
            aws_secret_access_key=aws_config["secret"]
        )

        # Download file from S3
        file_obj = s3.get_object(Bucket=bucket, Key=key)
        file_content = file_obj["Body"].read()

        # Process file using Unstructured API
        elements = partition(
            file=file_content,
            api_key=unstructured_config["api_key"],
            partition_endpoint=unstructured_config["endpoint"],
            strategy=strategy
        )

        # Prepare response
        return {
            "message": "File processing completed",
            "file": s3_path,
            "elements": [element.to_dict() for element in elements],
            "metadata": {
                "bucket": bucket,
                "key": key,
                "file_size": file_obj["ContentLength"],
                "content_type": file_obj["ContentType"]
            }
        }

    except Exception as e:
        logger.error(f"Error processing single file: {str(e)}")
        raise PipelineError(f"Error processing single file: {str(e)}")
