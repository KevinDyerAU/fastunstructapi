# Unstructured Workflow Python Client

A comprehensive Python client for creating and managing Unstructured workflows with S3 source connector, Supabase destination connector, high-resolution partitioner, page-based chunking, and OpenAI enrichment for images and tables.

## Features

- **S3 Source Connector**: Seamlessly connect to Amazon S3 buckets as data sources
- **Supabase Destination**: Store processed data in Supabase (PostgreSQL) with vector embeddings
- **High-Resolution Partitioner**: Advanced document parsing with `hi_res` strategy for optimal content extraction
- **Page-Based Chunking**: Intelligent document chunking by page for better context preservation
- **OpenAI Enrichment**: 
  - Image analysis and description generation using GPT-4 Vision
  - Table analysis and HTML conversion using GPT-4
- **Vector Embeddings**: Generate embeddings using OpenAI's `text-embedding-3-large` model
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Type Safety**: Full type hints and dataclass configurations

## Requirements

- Python 3.8+
- `unstructured-client` package
- Valid Unstructured API credentials
- AWS S3 access credentials
- Supabase database credentials
- OpenAI API access (configured through Unstructured)

## Installation

1. Install the required packages:

```bash
pip install unstructured-client python-dotenv
```

2. Set up your environment variables:

```bash
# Unstructured API credentials
export UNSTRUCTURED_API_KEY="your-api-key"
export UNSTRUCTURED_API_URL="your-api-url"

# AWS S3 credentials
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"

# Supabase credentials
export SUPABASE_HOST="your-project.supabase.co"
export SUPABASE_DB_NAME="postgres"
export SUPABASE_USERNAME="postgres"
export SUPABASE_PASSWORD="your-supabase-password"
```

Alternatively, create a `.env` file with these variables.

## Supabase Setup

Before using the client, you need to set up your Supabase database with the appropriate table schema. The client includes a helper function to generate the SQL schema:

```sql
-- Enable the pgvector extension for embeddings
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_elements_record_id ON elements(record_id);
CREATE INDEX IF NOT EXISTS idx_elements_element_id ON elements(element_id);
CREATE INDEX IF NOT EXISTS idx_elements_page_number ON elements(page_number);
CREATE INDEX IF NOT EXISTS idx_elements_partitioner_type ON elements(partitioner_type);
```

## Usage

### Basic Usage

```python
from unstructured_workflow_client import (
    UnstructuredWorkflowClient,
    S3SourceConfig,
    SupabaseDestinationConfig,
    WorkflowConfig
)

# Initialize the client
client = UnstructuredWorkflowClient()

# Configure S3 source
s3_config = S3SourceConfig(
    bucket_uri="s3://your-bucket-name/documents/",
    aws_access_key_id="your-aws-access-key",
    aws_secret_access_key="your-aws-secret-key",
    recursive=True
)

# Configure Supabase destination
supabase_config = SupabaseDestinationConfig(
    host="your-project.supabase.co",
    database_name="postgres",
    username="postgres",
    password="your-password",
    table_name="elements"
)

# Configure workflow
workflow_config = WorkflowConfig(
    name="Document-Processing-Workflow",
    source_config=s3_config,
    destination_config=supabase_config
)

# Create connectors and workflow
source_id = client.create_s3_source_connector(s3_config, "S3 Source")
dest_id = client.create_supabase_destination_connector(supabase_config, "Supabase Dest")
workflow = client.create_workflow(workflow_config, source_id, dest_id)

# Run the workflow
client.run_workflow(workflow["workflow_id"])
```

### Advanced Configuration

#### Custom Chunking Settings

The client uses optimized chunking settings by default, but you can modify the `_create_chunker_node()` method for custom requirements:

```python
def _create_chunker_node(self) -> WorkflowNode:
    return WorkflowNode(
        name="chunker",
        type="chunk",
        subtype="chunk",
        settings={
            "chunking_strategy": "by_page",
            "combine_text_under_n_chars": 3000,  # Combine small elements
            "include_orig_elements": True,       # Keep original elements
            "max_characters": 5500,              # Maximum chunk size
            "multipage_sections": True,          # Allow cross-page sections
            "new_after_n_chars": 3500,          # Start new chunk after N chars
            "overlap": 350,                      # Character overlap between chunks
            "overlap_all": True                  # Apply overlap to all chunks
        }
    )
```

#### Custom Enrichment Prompts

Modify the enrichment nodes for custom analysis:

```python
def _create_image_enrichment_node(self) -> WorkflowNode:
    return WorkflowNode(
        name="image_enrichment",
        type="enrich",
        subtype="image",
        settings={
            "provider": "openai",
            "model": "gpt-4-vision-preview",
            "prompt": "Analyze this image and extract all visible text, describe objects, and identify any charts or diagrams.",
            "max_tokens": 500,
            "temperature": 0.1
        }
    )
```

#### Scheduled Workflows

Create workflows that run on a schedule:

```python
workflow_config = WorkflowConfig(
    name="Scheduled-Processing",
    source_config=s3_config,
    destination_config=supabase_config,
    schedule="0 0 2 * * *",  # Run daily at 2 AM
    reprocess_all=False
)
```

## Workflow Components

### 1. Partitioner Node (High-Resolution)

The partitioner uses the `hi_res` strategy for advanced document analysis:

- **Strategy**: `hi_res` - Uses machine learning models for layout detection
- **Model**: `yolox` - Default model for object detection
- **Features**:
  - Table structure inference
  - Image extraction
  - Multi-language support
  - PDF table detection

### 2. Chunker Node (Page-Based)

Intelligent chunking that preserves document structure:

- **Strategy**: `by_page` - Maintains page boundaries
- **Overlap**: 350 characters between chunks for context preservation
- **Size Limits**: 3000-5500 characters per chunk
- **Features**:
  - Multipage section handling
  - Original element preservation
  - Smart text combination

### 3. Enrichment Nodes

#### Image Enrichment
- **Provider**: OpenAI GPT-4 Vision
- **Purpose**: Generate detailed descriptions of images
- **Output**: Text descriptions stored in `image_description` field

#### Table Enrichment
- **Provider**: OpenAI GPT-4
- **Purpose**: Analyze table content and structure
- **Output**: 
  - Text summaries in `table_description` field
  - HTML representations in `table_html` field

### 4. Embedder Node

- **Provider**: OpenAI
- **Model**: `text-embedding-3-large`
- **Dimensions**: 3072
- **Purpose**: Generate vector embeddings for semantic search

## API Reference

### UnstructuredWorkflowClient

#### `__init__(api_key: Optional[str] = None, server_url: Optional[str] = None)`

Initialize the client with API credentials.

#### `create_s3_source_connector(config: S3SourceConfig, connector_name: str) -> str`

Create an S3 source connector.

**Parameters:**
- `config`: S3 configuration object
- `connector_name`: Unique name for the connector

**Returns:** Connector ID string

#### `create_supabase_destination_connector(config: SupabaseDestinationConfig, connector_name: str) -> str`

Create a Supabase destination connector.

**Parameters:**
- `config`: Supabase configuration object
- `connector_name`: Unique name for the connector

**Returns:** Connector ID string

#### `create_workflow(config: WorkflowConfig, source_connector_id: str, destination_connector_id: str) -> Dict[str, Any]`

Create a complete workflow with all configurations.

**Parameters:**
- `config`: Workflow configuration object
- `source_connector_id`: ID of the source connector
- `destination_connector_id`: ID of the destination connector

**Returns:** Dictionary with workflow information

#### `run_workflow(workflow_id: str) -> Dict[str, Any]`

Run a workflow manually.

#### `get_workflow_status(workflow_id: str) -> Dict[str, Any]`

Get the current status of a workflow.

#### `list_workflows() -> List[Dict[str, Any]]`

List all workflows in the account.

### Configuration Classes

#### S3SourceConfig

```python
@dataclass
class S3SourceConfig:
    bucket_uri: str                          # s3://bucket-name/path/
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    recursive: bool = True
    custom_url: Optional[str] = None
```

#### SupabaseDestinationConfig

```python
@dataclass
class SupabaseDestinationConfig:
    host: str                    # Supabase database host
    database_name: str           # Database name (usually project reference)
    port: int = 5432
    username: str                # Usually 'postgres'
    password: str                # Database password
    table_name: str = "elements"
    batch_size: int = 100
```

#### WorkflowConfig

```python
@dataclass
class WorkflowConfig:
    name: str
    source_config: S3SourceConfig
    destination_config: SupabaseDestinationConfig
    schedule: Optional[str] = None      # Cron format
    reprocess_all: bool = False
```

## Error Handling

The client includes comprehensive error handling and logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

try:
    workflow = client.create_workflow(config, source_id, dest_id)
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Environment Variables

Always use environment variables for sensitive credentials:

```python
import os
from dotenv import load_dotenv

load_dotenv()

client = UnstructuredWorkflowClient(
    api_key=os.getenv("UNSTRUCTURED_API_KEY"),
    server_url=os.getenv("UNSTRUCTURED_API_URL")
)
```

### 2. Error Handling

Implement proper error handling for production use:

```python
try:
    workflow_result = client.create_workflow(config, source_id, dest_id)
    logger.info(f"Workflow created: {workflow_result['workflow_id']}")
except Exception as e:
    logger.error(f"Failed to create workflow: {e}")
    # Implement retry logic or fallback
```

### 3. Monitoring

Monitor workflow status regularly:

```python
import time

def wait_for_completion(client, workflow_id, timeout=3600):
    start_time = time.time()
    while time.time() - start_time < timeout:
        status = client.get_workflow_status(workflow_id)
        if status["status"] in ["completed", "failed"]:
            return status
        time.sleep(30)  # Check every 30 seconds
    raise TimeoutError("Workflow did not complete within timeout")
```

### 4. Batch Processing

For large datasets, consider processing in batches:

```python
# Process files in smaller batches
s3_config = S3SourceConfig(
    bucket_uri="s3://your-bucket/batch-1/",
    recursive=False  # Process one folder at a time
)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API keys are correct
   - Check environment variable names
   - Ensure API URL is correct

2. **S3 Connection Issues**
   - Verify AWS credentials
   - Check bucket permissions
   - Ensure bucket URI format is correct (`s3://bucket/path/`)

3. **Supabase Connection Issues**
   - Verify database credentials
   - Check network connectivity
   - Ensure pgvector extension is enabled

4. **Workflow Creation Failures**
   - Check connector IDs are valid
   - Verify workflow configuration
   - Review API response for specific errors

### Debug Mode

Enable debug logging for detailed information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Check the [Unstructured Documentation](https://docs.unstructured.io/)
- Join the [Unstructured Community](https://unstructured.io/community)
- Contact [Unstructured Support](mailto:support@unstructured.io)

## Changelog

### Version 1.0.0
- Initial release
- S3 source connector support
- Supabase destination connector support
- High-resolution partitioner
- Page-based chunking
- OpenAI image and table enrichment
- Vector embeddings with OpenAI
- Comprehensive logging and error handling

