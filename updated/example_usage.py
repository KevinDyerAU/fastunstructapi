#!/usr/bin/env python3
"""
Example Usage of Unstructured Workflow Python Client

This script demonstrates how to use the UnstructuredWorkflowClient
to create a complete document processing workflow with S3 source,
Supabase destination, and OpenAI enrichment.

Before running this script:
1. Copy .env.example to .env and fill in your credentials
2. Set up your Supabase database with the provided schema
3. Ensure your S3 bucket contains documents to process

Author: Manus AI
"""

import os
import time
import logging
from dotenv import load_dotenv

from unstructured_workflow_client import (
    UnstructuredWorkflowClient,
    S3SourceConfig,
    SupabaseDestinationConfig,
    WorkflowConfig,
    create_sample_supabase_table_schema
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    # Verify required environment variables
    required_vars = [
        "UNSTRUCTURED_API_KEY",
        "UNSTRUCTURED_API_URL",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "SUPABASE_HOST",
        "SUPABASE_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    logger.info("Environment variables loaded successfully")


def create_workflow_example():
    """
    Example function demonstrating complete workflow creation and execution.
    """
    logger.info("Starting workflow creation example")
    
    # Initialize the client
    client = UnstructuredWorkflowClient()
    
    # Configure S3 source
    s3_config = S3SourceConfig(
        bucket_uri=os.getenv("S3_BUCKET_URI", "s3://your-bucket-name/documents/"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),  # Optional
        recursive=True
    )
    
    # Configure Supabase destination
    supabase_config = SupabaseDestinationConfig(
        host=os.getenv("SUPABASE_HOST"),
        database_name=os.getenv("SUPABASE_DB_NAME", "postgres"),
        username=os.getenv("SUPABASE_USERNAME", "postgres"),
        password=os.getenv("SUPABASE_PASSWORD"),
        table_name="elements",
        batch_size=100
    )
    
    # Configure workflow
    workflow_config = WorkflowConfig(
        name="Document-Processing-Pipeline",
        source_config=s3_config,
        destination_config=supabase_config,
        schedule=None,  # Manual execution
        reprocess_all=False
    )
    
    try:
        # Step 1: Create source connector
        logger.info("Creating S3 source connector...")
        source_id = client.create_s3_source_connector(
            s3_config, 
            "S3 Document Source"
        )
        logger.info(f"S3 source connector created: {source_id}")
        
        # Step 2: Create destination connector
        logger.info("Creating Supabase destination connector...")
        dest_id = client.create_supabase_destination_connector(
            supabase_config, 
            "Supabase Vector Store"
        )
        logger.info(f"Supabase destination connector created: {dest_id}")
        
        # Step 3: Create workflow
        logger.info("Creating workflow with all configurations...")
        workflow_result = client.create_workflow(
            workflow_config, 
            source_id, 
            dest_id
        )
        
        logger.info("Workflow created successfully!")
        logger.info(f"Workflow ID: {workflow_result['workflow_id']}")
        logger.info(f"Workflow Name: {workflow_result['name']}")
        logger.info(f"Status: {workflow_result['status']}")
        
        # Step 4: Run the workflow
        logger.info("Initiating workflow run...")
        run_result = client.run_workflow(workflow_result["workflow_id"])
        logger.info(f"Workflow run initiated: {run_result}")
        
        # Step 5: Monitor workflow status
        logger.info("Monitoring workflow status...")
        workflow_id = workflow_result["workflow_id"]
        
        # Check status every 30 seconds for up to 10 minutes
        max_wait_time = 600  # 10 minutes
        check_interval = 30  # 30 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = client.get_workflow_status(workflow_id)
            logger.info(f"Current status: {status['status']}")
            
            if status["status"] in ["completed", "failed", "error"]:
                logger.info(f"Workflow finished with status: {status['status']}")
                break
            
            logger.info(f"Waiting {check_interval} seconds before next check...")
            time.sleep(check_interval)
        else:
            logger.warning("Workflow monitoring timed out")
        
        return workflow_result
        
    except Exception as e:
        logger.error(f"Error in workflow creation: {str(e)}")
        raise


def list_existing_workflows():
    """List all existing workflows in the account."""
    logger.info("Listing existing workflows...")
    
    client = UnstructuredWorkflowClient()
    
    try:
        workflows = client.list_workflows()
        
        if not workflows:
            logger.info("No workflows found")
            return
        
        logger.info(f"Found {len(workflows)} workflows:")
        for workflow in workflows:
            logger.info(f"  - {workflow['name']} (ID: {workflow['workflow_id']}, Status: {workflow['status']})")
        
        return workflows
        
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise


def print_supabase_schema():
    """Print the recommended Supabase table schema."""
    logger.info("Recommended Supabase table schema:")
    print("\n" + "="*60)
    print("SUPABASE TABLE SCHEMA")
    print("="*60)
    print(create_sample_supabase_table_schema())
    print("="*60 + "\n")


def main():
    """Main execution function."""
    print("Unstructured Workflow Client Example")
    print("="*40)
    
    try:
        # Setup environment
        setup_environment()
        
        # Print Supabase schema for reference
        print_supabase_schema()
        
        # List existing workflows
        list_existing_workflows()
        
        # Ask user if they want to create a new workflow
        response = input("\nDo you want to create a new workflow? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            # Verify S3 bucket URI
            bucket_uri = input("Enter your S3 bucket URI (e.g., s3://your-bucket/path/): ").strip()
            if bucket_uri:
                os.environ["S3_BUCKET_URI"] = bucket_uri
            
            # Create and run workflow
            workflow_result = create_workflow_example()
            
            print(f"\nWorkflow created successfully!")
            print(f"Workflow ID: {workflow_result['workflow_id']}")
            print(f"You can monitor this workflow in the Unstructured UI")
            
        else:
            logger.info("Skipping workflow creation")
        
        logger.info("Example completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

