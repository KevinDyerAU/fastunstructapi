# FastUnstructAPI

A document processing API that integrates with AWS S3, Unstructured.io, and Supabase for document ingestion, processing, and storage.

## Overview

FastUnstructAPI is a Flask-based API service that provides document processing capabilities using Unstructured.io's document processing pipeline. The service is designed to:

1. Ingest documents from AWS S3
2. Process documents using Unstructured.io's API
3. Store processed data in Supabase PostgreSQL database

## Features

- Document ingestion from AWS S3
- Support for multiple document types (PDF, DOCX, etc.)
- Configurable chunking and partitioning strategies
- Secure credential management
- Async processing support
- RESTful API endpoints

## Setup and Configuration

### Prerequisites

- Python 3.8+
- AWS S3 credentials
- Unstructured.io API key
- Supabase credentials

### Environment Variables

The following environment variables must be set:

```bash
AWS_S3_KEY=your_aws_access_key
AWS_S3_SECRET=your_aws_secret_key
UNSTRUCT_API_KEY=your_unstructured_api_key
SUPABASE_PASSWORD=your_supabase_password
```

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## API Endpoints

### Root Endpoint

```
GET /
```

Returns a health check message.

### Process Endpoint

```
POST /process
```

Process documents from S3:

```json
{
    "folder": "s3://your-bucket/path/to/folder",
    "strategy": "hi_res"  # Optional: auto, fast, hi_res, ocr_only, vlm
}
```

### Access Endpoint

```
POST /access
```

Process documents with explicit credentials:

```json
{
    "fileName": "path/to/file",
    "awsK": "your_aws_key",
    "awsS": "your_aws_secret",
    "unstrK": "your_unstructured_key",
    "supaK": "your_supabase_password",
    "strategy": "hi_res"  # Optional: auto, fast, hi_res, ocr_only, vlm
}
```

### Single File Processing Endpoint

```
POST /process_single
```

Process a single file from S3. This endpoint returns the processed elements directly instead of storing them in the database.

Example request:

```json
{
    "s3Path": "s3://your-bucket/path/to/file.pdf",
    "awsK": "your_aws_key",
    "awsS": "your_aws_secret",
    "unstrK": "your_unstructured_key",
    "strategy": "hi_res"  # Optional: auto, fast, hi_res, ocr_only, vlm
}
```

Example response:

```json
{
    "message": "File processing completed",
    "file": "s3://your-bucket/path/to/file.pdf",
    "elements": [
        {
            "type": "Title",
            "text": "Document Title",
            "metadata": {
                "page_number": 1,
                "coordinates": [...]
            }
        },
        {...}
    ],
    "metadata": {
        "bucket": "your-bucket",
        "key": "path/to/file.pdf",
        "file_size": 123456,
        "content_type": "application/pdf"
    }
}
```

### Available Parsing Strategies

The API supports several parsing strategies for document processing:

- `auto`: Automatically chooses the best strategy based on document characteristics (default)
- `fast`: Uses rule-based techniques for quick text extraction (not recommended for image-based files)
- `hi_res`: Uses advanced models to identify document layout and elements (recommended for high-quality processing)
- `ocr_only`: Uses OCR for image-based files
- `vlm`: Uses vision language models for image-based files (.bmp, .gif, .heic, .jpeg, .jpg, .pdf, .png, .tiff, .webp)

## Project Structure

```
fastunstructapi/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── pipeline.py
├── requirements.txt
└── README.md
```

## Development

Run the development server:

```bash
python -m src.main
```

## Deployment

The application can be deployed using Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

## Security

- All sensitive credentials are managed through environment variables
- No hardcoded credentials in the codebase
- Input validation is enforced
- Error handling is implemented

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.