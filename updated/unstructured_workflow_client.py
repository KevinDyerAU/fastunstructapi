#!/usr/bin/env python3
"""
Unstructured Workflow Python Client

A comprehensive Python client for creating and managing Unstructured workflows
with S3 source connector, Supabase (PostgreSQL) destination connector,
high-resolution partitioner, page-based chunking, and OpenAI enrichment
for images and tables.

Requirements:
- unstructured-client
- python-dotenv (optional, for environment variable management)

Author: Manus AI
Created: 2025-07-06
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from unstructured_client import UnstructuredClient
    from unstructured_client.models.shared import (
        WorkflowNode,
        CreateWorkflow,
        WorkflowType,
        Schedule
    )
    from unstructured_client.models.operations import CreateWorkflowRequest
except ImportError as e:
    raise ImportError(
        "Required package 'unstructured-client' not found. "
        "Install it with: pip install unstructured-client"
    ) from e

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class S3SourceConfig:
    """Configuration for S3 source connector."""
    bucket_uri: str  # Format: s3://bucket-name/path/
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    recursive: bool = True
    custom_url: Optional[str] = None


@dataclass
class SupabaseDestinationConfig:
    """Configuration for Supabase (PostgreSQL) destination connector."""
    host: str  # Supabase database host
    database_name: str  # Usually your project reference
    port: int = 5432
    username: str  # Usually 'postgres'
    password: str  # Your database password
    table_name: str = "elements"
    batch_size: int = 100


@dataclass
class WorkflowConfig:
    """Configuration for the workflow."""
    name: str
    source_config: S3SourceConfig
    destination_config: SupabaseDestinationConfig
    schedule: Optional[str] = None  # Cron format or None for manual runs
    reprocess_all: bool = False


class UnstructuredWorkflowClient:
    """
    A comprehensive client for creating and managing Unstructured workflows.
    
    This client provides methods to:
    - Create S3 source connectors
    - Create Supabase (PostgreSQL) destination connectors
    - Create workflows with high-res partitioner, page chunking, and OpenAI enrichment
    - Run and monitor workflows
    """
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        """
        Initialize the Unstructured workflow client.
        
        Args:
            api_key: Unstructured API key. If None, will use UNSTRUCTURED_API_KEY env var.
            server_url: Unstructured API URL. If None, will use UNSTRUCTURED_API_URL env var.
        """
        self.api_key = api_key or os.getenv("UNSTRUCTURED_API_KEY")
        self.server_url = server_url or os.getenv("UNSTRUCTURED_API_URL")
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Set UNSTRUCTURED_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        if not self.server_url:
            raise ValueError(
                "Server URL is required. Set UNSTRUCTURED_API_URL environment variable "
                "or pass server_url parameter."
            )
        
        self.client = UnstructuredClient(
            api_key_auth=self.api_key,
            server_url=self.server_url
        )
        logger.info("Unstructured client initialized successfully")
    
    def create_s3_source_connector(self, config: S3SourceConfig, connector_name: str) -> str:
        """
        Create an S3 source connector.
        
        Args:
            config: S3 source configuration
            connector_name: Unique name for the connector
            
        Returns:
            str: The connector ID
            
        Note:
            This is a placeholder implementation. In practice, you would use the
            Unstructured API to create the actual connector. The exact API endpoint
            and parameters may vary based on the current API version.
        """
        logger.info(f"Creating S3 source connector: {connector_name}")
        
        # Validate S3 configuration
        if not config.bucket_uri.startswith('s3://'):
            raise ValueError("Bucket URI must start with 's3://'")
        
        # In a real implementation, you would make an API call here
        # For now, we'll return a placeholder ID
        connector_id = f"s3_source_{connector_name.lower().replace(' ', '_')}"
        
        logger.info(f"S3 source connector created with ID: {connector_id}")
        return connector_id
    
    def create_supabase_destination_connector(
        self, 
        config: SupabaseDestinationConfig, 
        connector_name: str
    ) -> str:
        """
        Create a Supabase (PostgreSQL) destination connector.
        
        Args:
            config: Supabase destination configuration
            connector_name: Unique name for the connector
            
        Returns:
            str: The connector ID
            
        Note:
            This is a placeholder implementation. In practice, you would use the
            Unstructured API to create the actual connector.
        """
        logger.info(f"Creating Supabase destination connector: {connector_name}")
        
        # Validate Supabase configuration
        if not config.host:
            raise ValueError("Host is required for Supabase connection")
        if not config.database_name:
            raise ValueError("Database name is required")
        if not config.username:
            raise ValueError("Username is required")
        if not config.password:
            raise ValueError("Password is required")
        
        # In a real implementation, you would make an API call here
        connector_id = f"supabase_dest_{connector_name.lower().replace(' ', '_')}"
        
        logger.info(f"Supabase destination connector created with ID: {connector_id}")
        return connector_id
    
    def _create_partitioner_node(self) -> WorkflowNode:
        """
        Create a high-resolution partitioner node.
        
        Returns:
            WorkflowNode: Configured partitioner node
        """
        return WorkflowNode(
            name="partitioner",
            type="partition",
            subtype="partition",
            settings={
                "strategy": "hi_res",  # High-resolution partitioning
                "model_name": "yolox",  # Default model for hi_res
                "infer_table_structure": True,
                "extract_images": True,
                "extract_image_block_types": ["Image", "Table"],
                "languages": ["eng"],  # English language
                "pdf_infer_table_structure": True,
                "skip_infer_table_types": [],
                "xml_keep_tags": False
            }
        )
    
    def _create_chunker_node(self) -> WorkflowNode:
        """
        Create a page-based chunker node.
        
        Returns:
            WorkflowNode: Configured chunker node
        """
        return WorkflowNode(
            name="chunker",
            type="chunk",
            subtype="chunk",
            settings={
                "chunking_strategy": "by_page",  # Page-based chunking
                "combine_text_under_n_chars": 3000,
                "include_orig_elements": True,
                "max_characters": 5500,
                "multipage_sections": True,
                "new_after_n_chars": 3500,
                "overlap": 350,
                "overlap_all": True
            }
        )
    
    def _create_image_enrichment_node(self) -> WorkflowNode:
        """
        Create an image enrichment node using OpenAI.
        
        Returns:
            WorkflowNode: Configured image enrichment node
        """
        return WorkflowNode(
            name="image_enrichment",
            type="enrich",
            subtype="image",
            settings={
                "provider": "openai",
                "model": "gpt-4-vision-preview",  # OpenAI model for image analysis
                "prompt": "Provide a detailed description of this image, including any text, objects, people, and context visible in the image.",
                "max_tokens": 500,
                "temperature": 0.1
            }
        )
    
    def _create_table_enrichment_node(self) -> WorkflowNode:
        """
        Create a table enrichment node using OpenAI.
        
        Returns:
            WorkflowNode: Configured table enrichment node
        """
        return WorkflowNode(
            name="table_enrichment",
            type="enrich",
            subtype="table",
            settings={
                "provider": "openai",
                "model": "gpt-4",  # OpenAI model for table analysis
                "prompt": "Analyze this table and provide a summary of its contents, structure, and key insights. Include information about columns, data types, and any notable patterns or trends.",
                "max_tokens": 1000,
                "temperature": 0.1,
                "output_format": "html"  # Generate HTML representation
            }
        )
    
    def _create_embedder_node(self) -> WorkflowNode:
        """
        Create an embedder node for generating vector embeddings.
        
        Returns:
            WorkflowNode: Configured embedder node
        """
        return WorkflowNode(
            name="embedder",
            type="embed",
            subtype="embed",
            settings={
                "provider": "openai",
                "model": "text-embedding-3-large",
                "dimensions": 3072,
                "batch_size": 100
            }
        )
    
    def create_workflow(
        self, 
        config: WorkflowConfig,
        source_connector_id: str,
        destination_connector_id: str
    ) -> Dict[str, Any]:
        """
        Create a complete workflow with all specified configurations.
        
        Args:
            config: Workflow configuration
            source_connector_id: ID of the S3 source connector
            destination_connector_id: ID of the Supabase destination connector
            
        Returns:
            Dict[str, Any]: Workflow creation response
        """
        logger.info(f"Creating workflow: {config.name}")
        
        # Create workflow nodes in the correct order
        workflow_nodes = [
            self._create_partitioner_node(),
            self._create_chunker_node(),
            self._create_image_enrichment_node(),
            self._create_table_enrichment_node(),
            self._create_embedder_node()
        ]
        
        # Create schedule if specified
        schedule = None
        if config.schedule:
            schedule = Schedule(config.schedule)
        
        # Create the workflow
        workflow = CreateWorkflow(
            name=config.name,
            source_id=source_connector_id,
            destination_id=destination_connector_id,
            workflow_type=WorkflowType.CUSTOM,  # Custom workflow for fine-tuned settings
            workflow_nodes=workflow_nodes,
            schedule=schedule
        )
        
        # Create the workflow request
        request = CreateWorkflowRequest(create_workflow=workflow)
        
        try:
            response = self.client.workflows.create_workflow(request=request)
            workflow_info = response.workflow_information
            
            logger.info(f"Workflow created successfully:")
            logger.info(f"  Name: {workflow_info.name}")
            logger.info(f"  ID: {workflow_info.id}")
            logger.info(f"  Status: {workflow_info.status}")
            logger.info(f"  Type: {workflow_info.workflow_type}")
            
            return {
                "workflow_id": workflow_info.id,
                "name": workflow_info.name,
                "status": workflow_info.status,
                "workflow_type": workflow_info.workflow_type,
                "sources": [str(source) for source in workflow_info.sources],
                "destinations": [str(dest) for dest in workflow_info.destinations]
            }
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {str(e)}")
            raise
    
    def run_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Run a workflow manually.
        
        Args:
            workflow_id: ID of the workflow to run
            
        Returns:
            Dict[str, Any]: Workflow run response
        """
        logger.info(f"Running workflow: {workflow_id}")
        
        try:
            response = self.client.workflows.run_workflow(workflow_id=workflow_id)
            
            logger.info(f"Workflow run initiated successfully")
            return {"status": "running", "workflow_id": workflow_id}
            
        except Exception as e:
            logger.error(f"Failed to run workflow: {str(e)}")
            raise
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dict[str, Any]: Workflow status information
        """
        try:
            response = self.client.workflows.get_workflow(workflow_id=workflow_id)
            workflow_info = response.workflow_information
            
            return {
                "workflow_id": workflow_info.id,
                "name": workflow_info.name,
                "status": workflow_info.status,
                "workflow_type": workflow_info.workflow_type,
                "created_at": str(workflow_info.created_at) if hasattr(workflow_info, 'created_at') else None,
                "updated_at": str(workflow_info.updated_at) if hasattr(workflow_info, 'updated_at') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            raise
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.
        
        Returns:
            List[Dict[str, Any]]: List of workflow information
        """
        try:
            response = self.client.workflows.list_workflows()
            
            workflows = []
            for workflow in response.workflows:
                workflows.append({
                    "workflow_id": workflow.id,
                    "name": workflow.name,
                    "status": workflow.status,
                    "workflow_type": workflow.workflow_type
                })
            
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {str(e)}")
            raise


def create_sample_supabase_table_schema() -> str:
    """
    Generate a sample SQL schema for creating a table in Supabase
    that's compatible with Unstructured output.
    
    Returns:
        str: SQL CREATE TABLE statement
    """
    return """
-- Sample Supabase table schema for Unstructured workflow output
-- This table includes pgvector extension for embeddings storage

-- Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the elements table
CREATE TABLE IF NOT EXISTS elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id VARCHAR(255),
    element_id VARCHAR(255),
    text TEXT,
    embeddings VECTOR(3072), -- OpenAI text-embedding-3-large dimensions
    parent_id VARCHAR(255),
    page_number INTEGER,
    is_continuation BOOLEAN DEFAULT FALSE,
    orig_elements TEXT,
    partitioner_type VARCHAR(100),
    image_description TEXT, -- For image enrichment
    table_description TEXT, -- For table enrichment
    table_html TEXT, -- For table HTML representation
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_elements_record_id ON elements(record_id);
CREATE INDEX IF NOT EXISTS idx_elements_element_id ON elements(element_id);
CREATE INDEX IF NOT EXISTS idx_elements_page_number ON elements(page_number);
CREATE INDEX IF NOT EXISTS idx_elements_partitioner_type ON elements(partitioner_type);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_elements_updated_at 
    BEFORE UPDATE ON elements 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
"""


def main():
    """
    Example usage of the UnstructuredWorkflowClient.
    """
    # Load environment variables if using python-dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Initialize the client
    client = UnstructuredWorkflowClient()
    
    # Configure S3 source
    s3_config = S3SourceConfig(
        bucket_uri="s3://your-bucket-name/documents/",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        recursive=True
    )
    
    # Configure Supabase destination
    supabase_config = SupabaseDestinationConfig(
        host=os.getenv("SUPABASE_HOST", "your-project.supabase.co"),
        database_name=os.getenv("SUPABASE_DB_NAME", "postgres"),
        username=os.getenv("SUPABASE_USERNAME", "postgres"),
        password=os.getenv("SUPABASE_PASSWORD"),
        table_name="elements",
        batch_size=100
    )
    
    # Configure workflow
    workflow_config = WorkflowConfig(
        name="S3-to-Supabase-Workflow",
        source_config=s3_config,
        destination_config=supabase_config,
        schedule=None,  # Manual runs only
        reprocess_all=False
    )
    
    try:
        # Create connectors
        source_id = client.create_s3_source_connector(s3_config, "S3 Document Source")
        dest_id = client.create_supabase_destination_connector(supabase_config, "Supabase Destination")
        
        # Create workflow
        workflow_result = client.create_workflow(workflow_config, source_id, dest_id)
        print(f"Workflow created: {workflow_result}")
        
        # Run workflow
        run_result = client.run_workflow(workflow_result["workflow_id"])
        print(f"Workflow run initiated: {run_result}")
        
        # Check status
        status = client.get_workflow_status(workflow_result["workflow_id"])
        print(f"Workflow status: {status}")
        
        # Print sample table schema
        print("\nSample Supabase table schema:")
        print(create_sample_supabase_table_schema())
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()

