# FastUnstructAPI

A document processing API that bridges your data with Unstructured.io's powerful document processing capabilities, enabling seamless integration with AWS S3 and Supabase for scalable document ingestion, processing, and storage.

> **Latest Update (July 2025)**: Refactored to use the new Unstructured Workflow Client for improved reliability and performance.

## Overview

FastUnstructAPI is a Flask-based API service that leverages Unstructured.io's industry-leading document processing technology to transform unstructured data into AI-ready formats. The service is designed to:

1. Ingest documents from AWS S3
2. Process documents using Unstructured.io's advanced document processing pipeline
3. Store processed data in Supabase PostgreSQL database

### About Unstructured.io

Unstructured.io is an award-winning platform recognized as a leader in enterprise data infrastructure. It helps businesses unlock value from unstructured data by transforming it into a format that large language models can understand. The platform is trusted by Fortune 1000 companies and has been recognized by Fast Company, Forbes AI50, CB Insights AI 100, and Gartner Cool Vendor.

## Features

- **Document Processing**: Extract structured data from various document formats (PDF, DOCX, etc.)
- **Workflow-based Processing**: Leverage the new Unstructured Workflow API for reliable document processing
- **Cloud Storage Integration**: Seamlessly connect with AWS S3 for document storage
- **Database Support**: Store processed data in Supabase PostgreSQL
- **RESTful API**: Simple HTTP endpoints for document processing and management
- **Flexible Configuration**: Environment-based configuration for easy deployment
- **Scalable Architecture**: Designed to handle both small and large document volumes

## Setup and Configuration

### Prerequisites

- Python 3.10+ (3.12.3 recommended)
- AWS S3 credentials (Access Key and Secret Key)
- Unstructured.io API key
- Supabase PostgreSQL connection details
- Git
- pip (Python package manager)

### Render Deployment

This project includes a `render.yaml` file for easy deployment to Render. Follow these steps:

1. **Fork this repository** to your GitHub account
2. **Create a new Web Service** on Render
3. **Connect your GitHub repository**
4. **Configure the service**:
   - Name: `fastunstructapi` (or your preferred name)
   - Region: Choose the closest to your users
   - Branch: `main` (or your preferred branch)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn src.main:app --timeout 240`
   - Plan: `Starter` (or higher for production)

5. **Set environment variables** in the Render dashboard:
   - `PYTHON_VERSION`: `3.12.3` (Required)
   - `PYTHONUNBUFFERED`: `true`
   - `PYTHONDONTWRITEBYTECODE`: `1`
   - `PYTHONFAULTHANDLER`: `1`
   - `AWS_S3_KEY`: Your AWS S3 access key
   - `AWS_S3_SECRET`: Your AWS S3 secret key
   - `UNSTRUCT_API_KEY`: Your Unstructured.io API key
   - `SUPABASE_PASSWORD`: Your Supabase database password

6. **Deploy** the application

> **Note**: The application will be available at `https://your-render-app.onrender.com` after deployment.

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/fastunstructapi.git
   cd fastunstructapi
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following content:
   ```env
   # AWS Configuration
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_SESSION_TOKEN=your_session_token  # Optional, for temporary credentials
   AWS_REGION=ap-southeast-2  # Default region

   # Unstructured.io Configuration
   UNSTRUCTURED_API_KEY=your_api_key
   UNSTRUCTURED_API_URL=https://api.unstructured.io  # Default API endpoint

   # Supabase Configuration
   SUPABASE_HOST=aws-0-ap-southeast-2.pooler.supabase.com
   SUPABASE_PORT=5432
   SUPABASE_USERNAME=postgres.your_username
   SUPABASE_PASSWORD=your_supabase_password
   SUPABASE_DATABASE=postgres
   SUPABASE_TABLE=elements  # Default table name for storing processed elements

   # Application Settings
   LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
   DEBUG=False  # Set to True for development
   ```

5. **Run the application**:
   ```bash
   python -m src.main
   ```
   The API will be available at `http://localhost:8080`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS S3 access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS S3 secret key |
| `UNSTRUCTURED_API_KEY` | Yes | Unstructured.io API key |
| `SUPABASE_PASSWORD` | Yes | Supabase database password |
| `PYTHON_VERSION` | Yes (Render) | Must be set to `3.12.3` |
| `PYTHONUNBUFFERED` | No | Set to `true` for better logging |
| `PYTHONDONTWRITEBYTECODE` | No | Set to `1` to prevent .pyc files |
| `PYTHONFAULTHANDLER` | No | Set to `1` for better error reporting |

### Server Configuration

For production deployments, it's recommended to use Gunicorn with multiple workers. The `render.yaml` file is already configured for this.

### API Endpoints

### Process Documents

Process all documents in an S3 folder:

```http
POST /process
Content-Type: application/json

{
  "folder": "s3://your-bucket/path/to/documents",
  "strategy": "hi_res"
}
```

**Response:**
```json
{
  "message": "Documents processed successfully",
  "folder": "s3://your-bucket/path/to/documents",
  "status": "completed",
  "workflow_id": "workflow_12345",
  "run_id": "run_67890"
}
```

### Process Single File

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

The API supports several parsing strategies for document processing, each with different performance characteristics and cost implications:

#### `auto` (Default)
- **Description**: Automatically selects the most appropriate strategy based on document characteristics
- **Performance**: Optimized for a balance of speed and accuracy
- **Cost**: Variable - depends on the automatically chosen strategy
- **Use Case**: General purpose when you're unsure which strategy to use
- **Best For**: Most standard documents where you want a good balance of performance and accuracy

#### `fast`
- **Description**: Uses rule-based techniques for quick text extraction
- **Performance**: Fastest option with lowest computational requirements
- **Cost**: Lowest cost option
- **Limitations**: Not suitable for image-based files or complex layouts
- **Best For**: Simple text documents with extractable text where speed is critical

#### `hi_res` (High Resolution)
- **Description**: Uses advanced models to identify document layout and elements
- **Performance**: Slower but provides highest accuracy for complex documents
- **Cost**: Higher computational cost due to advanced model inference
- **Best For**: Documents with complex layouts where accurate element identification is crucial
- **Note**: Falls back to `ocr_only` if the required models are not available

#### `ocr_only`
- **Description**: Uses Optical Character Recognition (OCR) for text extraction
- **Performance**: Slower than `fast` but necessary for image-based content
- **Cost**: Moderate - requires OCR processing
- **Best For**: Scanned documents or images containing text
- **Note**: Falls back to `fast` if Tesseract is not available and text is extractable

#### `vlm` (Vision Language Model)
- **Description**: Uses vision language models for image-based files
- **Performance**: Slowest option due to complex model inference
- **Cost**: Highest cost option - requires significant computational resources
- **Supported Formats**: .bmp, .gif, .heic, .jpeg, .jpg, .pdf, .png, .tiff, .webp
- **Best For**: Complex image-based documents where maximum accuracy is required

### Cost and Performance Summary

| Strategy | Speed | Cost | Best For |
|----------|-------|------|----------|
| `auto`   | Fast to Medium | Low to Medium | General purpose, most documents |
| `fast`   | Fastest | Lowest | Simple text documents with extractable text |
| `hi_res` | Slower | Higher | Complex layouts, accurate element identification |
| `ocr_only` | Medium | Medium | Scanned documents, image-based text |
| `vlm`    | Slowest | Highest | Complex image-based documents requiring maximum accuracy |

> **Note**: The actual cost will depend on your deployment environment and usage patterns. For high-volume processing, consider starting with `fast` and only using more expensive strategies when necessary.

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