"""Main application module for the FastUnstruct API."""
from flask import Flask, jsonify, request
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
    RunWorkflowRequest,
    GetJobRequest
)
import time
import asyncio
import requests
from typing import Optional

app = Flask(__name__)

@app.route("/")
def root() -> dict:
    """Root endpoint to check if the application is running.
    
    Returns:
        dict: A simple status message
    """
    return {"status": "success", "message": "FastUnstruct API is running"}

# Chunking and embedding are optional.
@app.route("/process", methods=["POST"])
async def process_file() -> dict:
    """Process a file from the provided parameters.
    
    Expected JSON payload:
        - fileName: S3 path to process (e.g., s3://bucket/folder/)
        - awsK: AWS access key
        - awsS: AWS secret key
        - unstrK: Unstructured API key
        - pineconeK: Pinecone API key
        - pineconeIndex: Pinecone index name
        - waitForCompletion: (optional) Boolean to wait for job completion (default: true)
        - webhookUrl: (optional) URL to send completion notifications
        
    Returns:
        dict: Status message with the result of the operation
    """
    try:
        data = request.get_json()
        required_fields = ["fileName", "awsK", "awsS", "unstrK", "pineconeK", "pineconeIndex"]
        
        if not all(field in data for field in required_fields):
            return {"status": "error", "message": "Missing required fields"}, 400
            
        file_name = data["fileName"]
        wait_for_completion = data.get("waitForCompletion", True)
        webhook_url = data.get("webhookUrl")
        
        result = await start_pipeline(
            folder=file_name,
            aws_key=data["awsK"],
            aws_secret=data["awsS"],
            unstructured_key=data["unstrK"],
            pinecone_key=data["pineconeK"],
            pinecone_index=data["pineconeIndex"],
            wait_for_completion=wait_for_completion,
            webhook_url=webhook_url
        )
        
        return {
            "status": "success",
            "message": f"File {file_name} processed successfully",
            "result": result
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500



async def poll_job_status(
    client: UnstructuredClient,
    job_id: str,
    max_wait_seconds: int = 3600,
    poll_interval: int = 10
) -> dict:
    """Poll job status until completion or timeout.
    
    Args:
        client: Unstructured client instance
        job_id: Job ID to poll
        max_wait_seconds: Maximum time to wait (default: 1 hour)
        poll_interval: Seconds between polls (default: 10 seconds)
        
    Returns:
        Final job information dictionary
    """
    start_time = time.time()
    elapsed = 0
    
    print(f"Polling job status for: {job_id}")
    
    while elapsed < max_wait_seconds:
        try:
            # Get job status
            job_response = client.jobs.get_job(
                request=GetJobRequest(job_id=job_id)
            )
            
            status = job_response.job_information.status
            print(f"Job {job_id} status: {status} (elapsed: {int(elapsed)}s)")
            
            # Check if job is complete
            if status in ["completed", "success"]:
                print(f"Job {job_id} completed successfully!")
                return {
                    "job_id": job_id,
                    "status": status,
                    "elapsed_seconds": int(elapsed),
                    "job_info": job_response.job_information
                }
            elif status in ["failed", "error"]:
                print(f"Job {job_id} failed!")
                return {
                    "job_id": job_id,
                    "status": status,
                    "elapsed_seconds": int(elapsed),
                    "error": "Job failed",
                    "job_info": job_response.job_information
                }
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
            elapsed = time.time() - start_time
            
        except Exception as e:
            print(f"Error polling job status: {str(e)}")
            await asyncio.sleep(poll_interval)
            elapsed = time.time() - start_time
    
    # Timeout reached
    print(f"Job {job_id} polling timeout after {max_wait_seconds}s")
    return {
        "job_id": job_id,
        "status": "timeout",
        "elapsed_seconds": int(elapsed),
        "error": "Polling timeout exceeded"
    }


async def send_webhook_notification(
    webhook_url: Optional[str],
    job_result: dict,
    namespace: str,
    s3_path: str
) -> None:
    """Send webhook notification with job results.
    
    Args:
        webhook_url: URL to send webhook to (if None, skips notification)
        job_result: Job result dictionary from polling
        namespace: Pinecone namespace used
        s3_path: Source S3 path
    """
    if not webhook_url:
        print("No webhook URL provided, skipping notification")
        return
    
    try:
        payload = {
            "event": "workflow_complete",
            "timestamp": time.time(),
            "job_id": job_result.get("job_id"),
            "status": job_result.get("status"),
            "elapsed_seconds": job_result.get("elapsed_seconds"),
            "namespace": namespace,
            "s3_path": s3_path,
            "error": job_result.get("error")
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Webhook notification sent successfully to {webhook_url}")
        else:
            print(f"Webhook notification failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending webhook notification: {str(e)}")


def extract_namespace_from_s3_path(s3_path: str) -> str:
    """Extract namespace from S3 path.
    
    Args:
        s3_path: S3 path (e.g., s3://bucket-name/folder/subfolder/)
        
    Returns:
        Namespace derived from the folder path
    """
    # Remove s3:// prefix and bucket name
    path = s3_path.replace('s3://', '')
    parts = path.split('/')
    
    # Skip bucket name (first part) and get folder path
    if len(parts) > 1:
        # Join folder parts, removing empty strings and trailing slashes
        folder_parts = [p for p in parts[1:] if p]
        namespace = '-'.join(folder_parts) if folder_parts else 'default'
    else:
        namespace = 'default'
    
    # Pinecone namespace requirements: lowercase alphanumeric and hyphens
    namespace = namespace.lower().replace('_', '-').replace(' ', '-')
    
    return namespace


async def start_pipeline(
    folder: str,
    aws_key: str,
    aws_secret: str,
    unstructured_key: str,
    pinecone_key: str,
    pinecone_index: str,
    wait_for_completion: bool = True,
    webhook_url: Optional[str] = None
) -> dict:
    """Start the processing workflow using Unstructured Workflow Endpoint.
    
    Args:
        folder: The S3 folder path to process (e.g., s3://bucket-name/path/)
        aws_key: AWS access key
        aws_secret: AWS secret key
        unstructured_key: Unstructured API key
        pinecone_key: Pinecone API key
        pinecone_index: Pinecone index name
        wait_for_completion: Whether to poll job status until completion
        webhook_url: Optional webhook URL for job completion notifications
        
    Returns:
        Dictionary with job information and status
    """
    # Initialize the Unstructured client
    client = UnstructuredClient(api_key_auth=unstructured_key)
    
    # Extract namespace from S3 folder path
    namespace = extract_namespace_from_s3_path(folder)
    print(f"Using Pinecone namespace: {namespace}")
    
    # Generate unique names with timestamp
    timestamp = int(time.time())
    source_name = f"s3-source-{timestamp}"
    destination_name = f"pinecone-dest-{timestamp}"
    workflow_name = f"workflow-{timestamp}"
    
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
        print(f"Created source connector: {source_id}")
        
        # Step 2: Create Pinecone destination connector
        destination_response = client.destinations.create_destination(
            request=CreateDestinationRequest(
                create_destination_connector=CreateDestinationConnector(
                    name=destination_name,
                    type="pinecone",
                    config={
                        "api_key": pinecone_key,
                        "index_name": pinecone_index,
                        "namespace": namespace
                    }
                )
            )
        )
        destination_id = destination_response.destination_connector_information.id
        print(f"Created Pinecone destination connector: {destination_id} with namespace: {namespace}")
        
        # Step 3: Define workflow nodes
        partitioner_node = WorkflowNode(
            name="Partitioner",
            type="partition",
            subtype="unstructured_api",
            settings={
                "strategy": "hi_res",
                "pdf_infer_table_structure": True,
                "include_page_breaks": True
            }
        )
        
        chunker_node = WorkflowNode(
            name="Chunker",
            type="chunk",
            subtype="chunk_by_title",
            settings={
                "include_orig_elements": False,
                "multipage_sections": True
            }
        )
        
        # Embeddings node for vector search with pgvector
        embeddings_node = WorkflowNode(
            name="Embeddings",
            type="embed",
            subtype="unstructured_api",
            settings={
                "embedding_provider": "langchain-openai",
                "embedding_model_name": "text-embedding-ada-002",
                "embedding_api_key": unstructured_key,  # Use same API key for embeddings
                # Metadata fields to include for vector search
                "metadata_fields": [
                    "filename",
                    "page_number",
                    "filetype",
                    "element_id"
                ]
            }
        )
        
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
                        chunker_node,
                        embeddings_node
                    ]
                )
            )
        )
        workflow_id = workflow_response.workflow_information.id
        print(f"Created workflow: {workflow_id}")
        
        # Step 5: Run the workflow
        job_response = client.workflows.run_workflow(
            request=RunWorkflowRequest(
                workflow_id=workflow_id
            )
        )
        job_id = job_response.job_information.id
        print(f"Started job: {job_id}")
        
        # Poll job status if requested
        if wait_for_completion:
            job_result = await poll_job_status(client, job_id)
            
            # Send webhook notification if URL provided
            if webhook_url:
                await send_webhook_notification(webhook_url, job_result, namespace, folder)
            
            return job_result
        else:
            return {
                "job_id": job_id,
                "status": "started",
                "message": "Job started, not waiting for completion"
            }
        
    except Exception as e:
        print(f"Error in workflow execution: {str(e)}")
        error_result = {
            "status": "error",
            "error": str(e)
        }
        
        # Send error notification if webhook URL provided
        if webhook_url:
            await send_webhook_notification(webhook_url, error_result, namespace, folder)
        
        raise
    

def create_app():
    return app

if __name__ == "__main__":
    import os
    import sys
    import signal
    import platform
    
    # Default to port 8080 for local development
    port = int(os.environ.get('PORT', 8080))
    
    def signal_handler(sig, frame):
        print('\nShutting down server...')
        sys.exit(0)
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Use threaded=False to avoid issues on Windows
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            threaded=False,
            use_reloader=False  # Disable reloader to avoid issues with Windows
        )
    except PermissionError:
        print(f"Error: Port {port} requires administrator privileges. Try a port number above 1024.")
        sys.exit(1)
    except OSError as e:
        if platform.system() == 'Windows' and e.winerror == 10038:
            print("\nServer stopped. This is a known issue on Windows when stopping the server.")
            print("You can safely ignore this message if you stopped the server intentionally.")
        else:
            print(f"\nError starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)