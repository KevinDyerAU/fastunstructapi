"""
Document processing pipeline implementation

This module implements the document processing pipeline using Unstructured.io's
components for ingestion, processing, and storage.
"""

from typing import List, Dict, Any, Optional
import logging
import io
import boto3
from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.fsspec.s3 import (
    S3IndexerConfig,
    S3DownloaderConfig,
    S3ConnectionConfig,
    S3AccessConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
from unstructured_ingest.v2.processes.connectors.sql.postgres import (
    PostgresConnectionConfig,
    PostgresAccessConfig,
    PostgresUploaderConfig,
    PostgresUploadStagerConfig
)
from unstructured.partition.api import partition


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


def create_pipeline_config(
    folder: str,
    aws_config: Dict[str, str],
    unstructured_config: Dict[str, str],
    supabase_config: Dict[str, str],
    strategy: str = "hi_res"
) -> Pipeline:
    """Create and configure the document processing pipeline

    Args:
        folder (str): S3 folder path to process
        aws_config (Dict[str, str]): AWS configuration
        unstructured_config (Dict[str, str]): Unstructured.io configuration
        supabase_config (Dict[str, str]): Supabase configuration
        strategy (str): Partitioning strategy to use (auto, fast, hi_res, ocr_only, vlm)

    Returns:
        Pipeline: Configured pipeline instance
    """
    try:
        pipeline = Pipeline.from_configs(
            context=ProcessorConfig(),
            indexer_config=S3IndexerConfig(remote_url=folder),
            downloader_config=S3DownloaderConfig(),
            source_connection_config=S3ConnectionConfig(
                access_config=S3AccessConfig(
                    key=aws_config["key"],
                    secret=aws_config["secret"]
                )
            ),
            partitioner_config=PartitionerConfig(
                partition_by_api=True,
                api_key=unstructured_config["api_key"],
                partition_endpoint=unstructured_config["endpoint"],
                strategy=strategy,
                additional_partition_args={
                    "split_pdf_page": True,
                    "split_pdf_allow_failed": True,
                    "split_pdf_concurrency_level": 15
                }
            ),
            chunker_config=ChunkerConfig(chunking_strategy="by_title"),
            destination_connection_config=PostgresConnectionConfig(
                access_config=PostgresAccessConfig(password=supabase_config["password"]),
                host=supabase_config["host"],
                port=supabase_config["port"],
                username=supabase_config["username"],
                database=supabase_config["database"]
            ),
            stager_config=PostgresUploadStagerConfig()
        )
        return pipeline
    except Exception as e:
        logger.error(f"Failed to create pipeline: {str(e)}")
        raise PipelineError(f"Failed to create pipeline: {str(e)}")


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
        pipeline = create_pipeline_config(
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
