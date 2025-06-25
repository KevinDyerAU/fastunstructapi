# FastUnstructAPI

A document processing API that bridges your data with Unstructured.io's powerful document processing capabilities, enabling seamless integration with AWS S3 and Supabase for scalable document ingestion, processing, and storage.

> **Latest Update (June 2025)**: Added support for Python 3.12.3 and updated deployment configuration for Render.

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

- Python 3.12.3 (Required for compatibility with dependencies)
- AWS S3 credentials
- Unstructured.io API key
- Supabase credentials
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
   # AWS S3 Credentials
   AWS_S3_KEY=your_aws_access_key
   AWS_S3_SECRET=your_aws_secret_key
   
   # Unstructured.io API Key
   UNSTRUCT_API_KEY=your_unstructured_api_key
   
   # Supabase Database Password
   SUPABASE_PASSWORD=your_supabase_database_password
   ```

5. **Run the application**:
   ```bash
   python -m src.main
   ```
   The API will be available at `http://localhost:8080`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_S3_KEY` | Yes | AWS S3 access key |
| `AWS_S3_SECRET` | Yes | AWS S3 secret key |
| `UNSTRUCT_API_KEY` | Yes | Unstructured.io API key |
| `SUPABASE_PASSWORD` | Yes | Supabase database password |
| `PYTHON_VERSION` | Yes (Render) | Must be set to `3.12.3` |
| `PYTHONUNBUFFERED` | No | Set to `true` for better logging |
| `PYTHONDONTWRITEBYTECODE` | No | Set to `1` to prevent .pyc files |
| `PYTHONFAULTHANDLER` | No | Set to `1` for better error reporting |

### Server Configuration

For production deployments, it's recommended to use Gunicorn with multiple workers. The `render.yaml` file is already configured for this.

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