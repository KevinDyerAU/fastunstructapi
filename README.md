# FastUnstructAPI

A document processing API that bridges your data with Unstructured.io's powerful document processing capabilities, enabling seamless integration with AWS S3 and Supabase for scalable document ingestion, processing, and storage.

## Overview

FastUnstructAPI is a Flask-based API service that leverages Unstructured.io's industry-leading document processing technology to transform unstructured data into AI-ready formats. The service is designed to:

1. Ingest documents from AWS S3
2. Process documents using Unstructured.io's advanced document processing pipeline
3. Store processed data in Supabase PostgreSQL database

### About Unstructured.io

Unstructured.io is an award-winning platform recognized as a leader in enterprise data infrastructure. It helps businesses unlock value from unstructured data by transforming it into a format that large language models can understand. The platform is trusted by Fortune 1000 companies and has been recognized by Fast Company, Forbes AI50, CB Insights AI 100, and Gartner Cool Vendor.

## Features

- Document ingestion from AWS S3
- Support for multiple document types (PDF, DOCX, etc.)
- Configurable chunking and partitioning strategies
- Secure credential management
- Async processing support
- RESTful API endpoints

## Setup and Configuration

### Prerequisites

- Python 3.11 (Required for Render deployment)
- AWS S3 credentials
- Unstructured.io API key
- Supabase credentials

### Render Deployment

To deploy this application on Render:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. In the Environment Variables section, set:
   - `AWS_S3_KEY`
   - `AWS_S3_SECRET`
   - `UNSTRUCT_API_KEY`
   - `SUPABASE_PASSWORD`

4. Under Build Command, use:
   ```bash
   pip install -r requirements.txt
   ```

5. Under Start Command, use:
   ```bash
   gunicorn src.main:app --timeout 240
   ```

6. Set the Python version in Render:
   - Go to the Environment Variables section
   - Add a new environment variable:
     - Key: `PYTHON_VERSION`
     - Value: `3.12.3`

Note: The application requires Python 3.12.3 for compatibility with the latest dependencies. This must be set as an environment variable named `PYTHON_VERSION` with a full version string (major.minor.patch) such as `3.12.3`. The patch version must be specified for proper deployment.

Important: Render will automatically set the `PORT` environment variable for your application. You don't need to set it manually. The application will use this port through the Gunicorn server configuration in the `render.yaml` file.

### Server Configuration

To run the Flask server locally:

```bash
python wsgi.py
```

The application will automatically use the port specified in the `PORT` environment variable, defaulting to port 80 if not specified.

Alternatively, you can run the application directly using:

```bash
python src/main.py
```

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

### Health Check Endpoint

```
GET /
```

Returns a health check message:

```json
{
    "Message": "app up and running successfully"
}
```

### Document Processing Endpoint

```
POST /access
```

Process documents from AWS S3 with explicit credentials. This endpoint requires the following JSON payload:

```json
{
    "fileName": "path/to/file"
}
```

The following environment variables must be set:
- `AWS_ACCESS_KEY_ID1`: AWS access key
- `AWS_SECRET_ACCESS_KEY1`: AWS secret key
- `UNSTRUCTURED_API_KEY`: Unstructured.io API key
- `SUPABASE_PASSWORD`: Supabase password

Example curl command:

```bash
# Replace YOUR_API_URL with your deployed API URL
# Replace YOUR_FILE_PATH with the S3 path to your file
curl -X POST YOUR_API_URL/access \
  -H "Content-Type: application/json" \
  -d '{"fileName": "YOUR_FILE_PATH"}'
```

Example response:

```json
{
    "Message": "Filename YOUR_FILE_PATH received and processed"
}
```

### Available Parsing Strategies

The API supports several parsing strategies for document processing:

- `auto`: Automatically chooses the best strategy based on document characteristics (default)
- `fast`: Uses rule-based techniques for quick text extraction (not recommended for image-based files)
- `hi_res`: Uses advanced models to identify document layout and elements (recommended for high-quality processing)
- `ocr_only`: Uses OCR for image-based files
- `vlm`: Uses vision language models for image-based files (.bmp, .gif, .heic, .jpeg, .jpg, .pdf, .png, .tiff, .webp)
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