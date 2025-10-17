"""Main application module for the FastUnstruct API.

This module provides a Flask API for processing unstructured documents
using the Unstructured Workflow Endpoint with S3 and PostgreSQL/Supabase integration.
"""
import os
import sys
import signal
import platform
import time
import logging
from typing import Dict, Any, Tuple

from flask import Flask, request
from unstructured_client import UnstructuredClient
from unstructured_client.models.shared import (
    CreateSourceConnector,
    CreateDestinationConnector,
    CreateWorkflow,
    WorkflowNode,
    WorkflowType
)
from unstructured_client.models.operations import (
    CreateSourceRequest,
    CreateDestinationRequest,
    CreateWorkflowRequest,
    RunWorkflowRequest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
VALID_STRATEGIES = {"auto", "fast", "hi_res", "ocr_only", "vlm"}
DEFAULT_STRATEGY = "hi_res"  # Best for complex documents with tables
DEFAULT_PORT = 8080
DEFAULT_BATCH_SIZE = 100

# Supabase Configuration
SUPABASE_HOST = "aws-0-ap-southeast-2.pooler.supabase.com"
SUPABASE_PORT = 6543
SUPABASE_USERNAME = "postgres.nwwqkubrlvmrycubylso"
SUPABASE_DATABASE = "postgres"
SUPABASE_TABLE = "elements"

app = Flask(__name__)

@app.route("/")
def root() -> Dict[str, str]:
    """Root endpoint to check if the application is running.
    
    Returns:
        dict: Status message indicating the API is operational
    """
    return {"status": "success", "message": "FastUnstruct API is running"}


@app.route("/process", methods=["POST"])
async def process_file() -> Tuple[Dict[str, Any], int]:
    """Process documents from S3 using Unstructured Workflow Endpoint.
    
    Expected JSON payload:
        - fileName (str): S3 path to process (e.g., s3://bucket/path/)
        - awsK (str): AWS access key
        - awsS (str): AWS secret key
        - unstrK (str): Unstructured API key
        - supaK (str): Supabase password
        - strategy (str, optional): Partitioning strategy (default: "hi_res")
          Options: "auto", "fast", "hi_res", "ocr_only", "vlm"
        
    Returns:
        tuple: (dict, status_code) containing result message and HTTP status
    """
    try:
        data = request.get_json()
        if not data:
            return {"status": "error", "message": "No JSON payload provided"}, 400
        
        # Validate required fields
        required_fields = ["fileName", "awsK", "awsS", "unstrK", "supaK"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
            
        file_name = data["fileName"]
        strategy = data.get("strategy", DEFAULT_STRATEGY)
        
        # Validate strategy parameter
        if strategy not in VALID_STRATEGIES:
            return {
                "status": "error",
                "message": f"Invalid strategy '{strategy}'. Must be one of: {', '.join(VALID_STRATEGIES)}"
            }, 400
        
        logger.info(f"Processing request for: {file_name} with strategy: {strategy}")
        
        await start_pipeline(
            folder=file_name,
            aws_key=data["awsK"],
            aws_secret=data["awsS"],
            unstructured_key=data["unstrK"],
            supabase_key=data["supaK"],
            strategy=strategy
        )
        
        return {
            "status": "success",
            "message": f"Workflow started for {file_name} with {strategy} strategy"
        }, 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"status": "error", "message": str(e)}, 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Internal server error: {str(e)}"}, 500


async def start_pipeline(
    folder: str,
    aws_key: str,
    aws_secret: str,
    unstructured_key: str,
    supabase_key: str,
    strategy: str = DEFAULT_STRATEGY
) -> None:
    """Start the processing workflow using Unstructured Workflow Endpoint.
    
    Creates source and destination connectors, defines workflow nodes,
    and executes the workflow as an asynchronous job.
    
    Args:
        folder: S3 folder path to process (e.g., s3://bucket-name/path/)
        aws_key: AWS access key for S3
        aws_secret: AWS secret access key
        unstructured_key: Unstructured API key from platform.unstructured.io
        supabase_key: Supabase PostgreSQL password
        strategy: Partitioning strategy ("hi_res", "fast", or "auto")
        
    Raises:
        Exception: If workflow creation or execution fails
    """
    client = UnstructuredClient(api_key_auth=unstructured_key)
    
    # Generate unique names with timestamp
    timestamp = int(time.time())
    source_name = f"s3-source-{timestamp}"
    destination_name = f"supabase-dest-{timestamp}"
    workflow_name = f"workflow-{timestamp}"
    
    logger.info(f"Initializing workflow: {workflow_name}")
    
    try:
        # Step 1: Create S3 source connector
        source_response = client.sources.create_source(
            request=CreateSourceRequest(
                create_source_connector=CreateSourceConnector(
                    name=source_name,
                    type="s3",
                    config={
                        "key": aws_key,
                        "secret": aws_secret,
                        "remote_url": folder,
                        "recursive": True
                    }
                )
            )
        )
        source_id = source_response.source_connector_information.id
        logger.info(f"Created S3 source connector: {source_id}")
        
        # Step 2: Create PostgreSQL/Supabase destination connector
        destination_response = client.destinations.create_destination(
            request=CreateDestinationRequest(
                create_destination_connector=CreateDestinationConnector(
                    name=destination_name,
                    type="postgres",
                    config={
                        "host": SUPABASE_HOST,
                        "port": SUPABASE_PORT,
                        "username": SUPABASE_USERNAME,
                        "database": SUPABASE_DATABASE,
                        "password": supabase_key,
                        "table_name": SUPABASE_TABLE,
                        "batch_size": DEFAULT_BATCH_SIZE
                    }
                )
            )
        )
        destination_id = destination_response.destination_connector_information.id
        logger.info(f"Created PostgreSQL destination connector: {destination_id}")
        
        # Step 3: Define workflow nodes with comprehensive metadata capture
        partitioner_node = WorkflowNode(
            name="Partitioner",
            type="partition",
            subtype="unstructured_api",
            settings={
                # Strategy configuration
                "strategy": strategy,
                
                # Table and structure detection
                "pdf_infer_table_structure": True,
                "include_page_breaks": True,
                
                # Metadata capture settings
                "coordinates": True,  # Capture element coordinates for position tracking
                "extract_image_block_types": ["Image", "Table"],  # Extract visual elements
                
                # Language detection for international documents
                "languages": ["eng"],  # Primary language, auto-detects others
                
                # Ensure unique IDs for tracking elements
                "unique_element_ids": True,
            }
        )
        
        chunker_node = WorkflowNode(
            name="Chunker",
            type="chunk",
            subtype="chunk_by_title",
            settings={
                # Preserve metadata through chunking
                "include_orig_elements": True,  # Keep original element metadata
                "multipage_sections": True,  # Allow chunks to span pages
                
                # Maintain parent-child relationships
                "max_characters": 1500,  # Optimal chunk size
                "new_after_n_chars": 1000,  # Start new chunk after N chars
                "overlap": 100,  # Character overlap between chunks for context
            }
        )
        
        logger.info(f"Configured partitioner with {strategy} strategy")
        
        # Step 4: Create workflow
        workflow_response = client.workflows.create_workflow(
            request=CreateWorkflowRequest(
                create_workflow=CreateWorkflow(
                    name=workflow_name,
                    source_id=source_id,
                    destination_id=destination_id,
                    workflow_type=WorkflowType.BATCH,
                    workflow_nodes=[
                        partitioner_node,
                        chunker_node
                    ]
                )
            )
        )
        workflow_id = workflow_response.workflow_information.id
        logger.info(f"Created workflow: {workflow_id}")
        
        # Step 5: Run the workflow
        job_response = client.workflows.run_workflow(
            request=RunWorkflowRequest(
                workflow_id=workflow_id
            )
        )
        job_id = job_response.job_information.id
        logger.info(f"Started job: {job_id}")
        logger.info(f"Monitor job at: https://platform.unstructured.io")
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
        raise

def create_app() -> Flask:
    """Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    return app


if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get('PORT', DEFAULT_PORT))
    
    def signal_handler(sig, frame):
        """Handle shutdown signals gracefully."""
        logger.info('Shutting down server...')
        sys.exit(0)
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting FastUnstruct API on port {port}")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            threaded=False,
            use_reloader=False
        )
    except PermissionError:
        logger.error(f"Port {port} requires administrator privileges. Try a port above 1024.")
        sys.exit(1)
    except OSError as e:
        if platform.system() == 'Windows' and hasattr(e, 'winerror') and e.winerror == 10038:
            logger.info("Server stopped (Windows shutdown behavior - can be safely ignored)")
        else:
            logger.error(f"Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)