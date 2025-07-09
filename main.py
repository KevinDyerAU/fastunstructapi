"""Main application module for the FastUnstruct API."""
from flask import Flask, jsonify, request
from unstructured_ingest.pipeline.pipeline import Pipeline
from unstructured_ingest.interfaces import ProcessorConfig
from unstructured_ingest.processes.connectors.fsspec.s3 import (
    S3IndexerConfig,
    S3DownloaderConfig,
    S3ConnectionConfig,
    S3AccessConfig
)
from unstructured_ingest.processes.partitioner import PartitionerConfig
from unstructured_ingest.processes.chunker import ChunkerConfig
from unstructured_ingest.processes.connectors.sql.postgres import (
    PostgresConnectionConfig,
    PostgresAccessConfig,
    PostgresUploadStagerConfig,
    PostgresUploaderConfig
)

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
        - fileName: Name of the file to process
        - awsK: AWS access key
        - awsS: AWS secret key
        - unstrK: Unstructured API key
        - supaK: Supabase API key
        
    Returns:
        dict: Status message with the result of the operation
    """
    try:
        data = request.get_json()
        required_fields = ["fileName", "awsK", "awsS", "unstrK", "supaK"]
        
        if not all(field in data for field in required_fields):
            return {"status": "error", "message": "Missing required fields"}, 400
            
        file_name = data["fileName"]
        
        await start_pipeline(
            folder=file_name,
            aws_key=data["awsK"],
            aws_secret=data["awsS"],
            unstructured_key=data["unstrK"],
            supabase_key=data["supaK"]
        )
        
        return {
            "status": "success",
            "message": f"File {file_name} processed successfully"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500



async def start_pipeline(
    folder: str,
    aws_key: str,
    aws_secret: str,
    unstructured_key: str,
    supabase_key: str
) -> None:
    """Start the processing pipeline for the given file.
    
    Args:
        folder: The folder path to process
        aws_key: AWS access key
        aws_secret: AWS secret key
        unstructured_key: Unstructured API key
        supabase_key: Supabase API key
    """
    # Metadata fields to include in the output
    metadata_fields = [
        # Core identification
        "id", "element_id", "type", "filename", "filetype",
        
        # Basic metadata
        "date_created", "date_modified", "page_number", "file_directory",
        
        # Content analysis
        "languages", "section", "category_depth",
        
        # Add these back if needed
        # "layout_width", "layout_height", "points", "header_footer_type",
        # "version", "system", "permissions_data", "record_locator",
        # "sent_from", "sent_to", "subject", "link_urls", "link_texts",
        # "emphasized_text_contents", "emphasized_text_tags", "text_as_html",
        # "regex_metadata", "detection_class_prob"
    ]

    # Configure and start the pipeline
    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=S3IndexerConfig(remote_url=folder),
        downloader_config=S3DownloaderConfig(),
        source_connection_config=S3ConnectionConfig(
            access_config=S3AccessConfig(
                key=aws_key,
                secret=aws_secret
            )
        ),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=unstructured_key,
            partition_endpoint='https://api.unstructuredapp.io/general/v0/general',
            strategy="hi_res",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            }
        ),
        chunker_config=ChunkerConfig(chunking_strategy="by_title"),
        destination_connection_config=PostgresConnectionConfig(
            access_config=PostgresAccessConfig(password=supabase_key),
            host='aws-0-ap-southeast-2.pooler.supabase.com',
            port='6543',
            username='postgres.nwwqkubrlvmrycubylso',
            database='postgres'
        ),
        stager_config=PostgresUploadStagerConfig(),
        uploader_config=PostgresUploaderConfig()
    ).run()
    

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