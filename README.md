# FastUnstruct API

A production-ready Flask API for processing unstructured documents using **Unstructured Workflow Endpoint**, with seamless S3 and PostgreSQL/Supabase integration. Features configurable partitioning strategies and enterprise-grade document processing.

## ✨ Features

- **🔄 Workflow Endpoint**: Uses Unstructured's modern workflow API with job-based processing
- **📦 Batch Processing**: Process multiple documents efficiently from S3 buckets
- **🎯 Configurable Strategies**: Choose between hi_res, fast, or auto partitioning (default: hi_res)
- **🔍 Advanced Partitioning**: Hi-res document partitioning with table structure inference
- **✂️ Smart Chunking**: By-title chunking strategy with multipage sections
- **☁️ S3 Integration**: Dynamic S3 source connectors for AWS document access
- **🗄️ PostgreSQL/Supabase**: Automated destination connectors for data storage
- **🌐 RESTful API**: Simple and intuitive API endpoints
- **🏢 Production Ready**: SOC2 compliant with enterprise-grade features
- **💰 Cost Optimized**: Built-in logic for best quality/cost ratio
- **⚡ Asynchronous Jobs**: Non-blocking workflow execution

## 🏗️ Workflow Architecture

This application uses the **Unstructured Workflow Endpoint** architecture, which provides production-ready document processing with better performance and cost optimization.

```mermaid
graph TD
    A["🌐 API Request<br/>POST /process"] --> B["🔑 Initialize<br/>UnstructuredClient"]
    B --> C["📁 Create S3<br/>Source Connector"]
    C --> D["🗄️ Create PostgreSQL<br/>Destination Connector"]
    D --> E["⚙️ Define Workflow Nodes"]
    
    E --> F["📄 Partitioner Node<br/>(Strategy: hi_res/fast/auto/ocr_only/vlm)"]
    E --> G["✂️ Chunker Node<br/>(By-Title Strategy)"]
    
    F --> |"Hi-Res Strategy<br/>Table Inference<br/>Page Breaks"| H["🔧 Create Workflow"]
    G --> |"Multipage Sections<br/>Semantic Chunking"| H
    
    H --> I["▶️ Run Workflow"]
    I --> J["📋 Job Created<br/>(Async)"]
    J --> K["☁️ S3 Batch<br/>Processing"]
    K --> L["🔍 Document<br/>Partitioning"]
    L --> M["✂️ Content<br/>Chunking"]
    M --> N["💾 Store in<br/>PostgreSQL/Supabase"]
    N --> O["✅ API Response<br/>Job ID & Status"]
    
    style A fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    style O fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style F fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style G fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style J fill:#ffe0b2,stroke:#f57c00,stroke-width:2px
```

### How It Works

1. **🔌 Source Connector**: Creates a dynamic S3 connector with your AWS credentials to access documents
2. **🎯 Destination Connector**: Creates a PostgreSQL connector for Supabase to store processed data
3. **⚙️ Workflow Nodes**:
   - **Partitioner**: Extracts structured content using configurable strategy (hi_res, fast, or auto)
   - **Chunker**: Splits content into semantic chunks using by-title strategy
4. **▶️ Job Execution**: Runs the workflow asynchronously and returns job information
5. **📦 Batch Processing**: Processes all files in the S3 folder recursively

### 🆚 Why Workflow Endpoint?

**Key Advantages:**
- ✅ Uses `unstructured-client` SDK (not deprecated `unstructured-ingest`)
- ✅ Production endpoint: `https://platform.unstructured.io/api/v1`
- ✅ Job-based asynchronous processing (not synchronous)
- ✅ Better performance with latest vision transformer models
- ✅ Cost-optimized with intelligent routing
- ✅ SOC2, HIPAA, GDPR, ISO 27001 compliant

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- AWS credentials (for S3 access)
- Unstructured.io API key (get one at [platform.unstructured.io](https://platform.unstructured.io))
- PostgreSQL database (Supabase recommended)

## 🛠 Local Development

### 1. Clone the repository

```bash
git clone https://github.com/KevinDyerAU/fastunstructapi.git
cd fastunstructapi
```

### 2. Set up a virtual environment

#### Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_APP=wsgi:app
FLASK_ENV=development
PORT=8080

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Unstructured.io Configuration
UNSTRUCTURED_API_KEY=your_unstructured_api_key

# PostgreSQL Configuration (Supabase)
SUPABASE_DATABASE_URL=postgresql://user:password@host:port/dbname
SUPABASE_PASSWORD=your_supabase_password
```

### 5. Run the development server

```bash
python main.py
```

The API will be available at `http://localhost:8080`

## 🚀 Deployment

### Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/KevinDyerAU/fastunstructapi)

1. Click the "Deploy to Render" button above
2. Configure your environment variables in the Render dashboard
3. Deploy!

Required environment variables in Render:
- `PORT`: The port the app should listen on (set automatically by Render)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `UNSTRUCTURED_API_KEY`: Your Unstructured.io API key
- `SUPABASE_DATABASE_URL`: Your Supabase PostgreSQL connection string
- `SUPABASE_PASSWORD`: Your Supabase password

### Manual Deployment

1. Clone the repository
2. Set up a Python virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables (see Configuration section)
5. Run with Uvicorn: `uvicorn wsgi:app --host 0.0.0.0 --port $PORT`

## 🌐 API Endpoints

### Root Endpoint

Check if the API is running:

```http
GET /
```

**Response:**
```json
{
  "status": "success",
  "message": "FastUnstruct API is running"
}
```

### Process Documents (Workflow Endpoint)

Process documents from S3 using the Unstructured Workflow Endpoint:

```http
POST /process
Content-Type: application/json

{
  "fileName": "s3://bucket-name/folder/path/",
  "awsK": "your_aws_access_key",
  "awsS": "your_aws_secret_key",
  "unstrK": "your_unstructured_api_key",
  "supaK": "your_supabase_password",
  "strategy": "hi_res"
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fileName` | string | ✅ Yes | - | S3 path to folder or file (e.g., `s3://my-bucket/documents/`) |
| `awsK` | string | ✅ Yes | - | AWS access key for S3 access |
| `awsS` | string | ✅ Yes | - | AWS secret access key |
| `unstrK` | string | ✅ Yes | - | Unstructured API key from [platform.unstructured.io](https://platform.unstructured.io) |
| `supaK` | string | ✅ Yes | - | Supabase PostgreSQL password |
| `strategy` | string | ❌ No | `"hi_res"` | Partitioning strategy: `"auto"`, `"fast"`, `"hi_res"`, `"ocr_only"`, or `"vlm"` |

**Strategy Options:**

- **`hi_res`** (default): High-resolution model-based partitioning
  - Best for: Complex documents, tables, forms, multi-column layouts
  - Processing time: Slower but most accurate
  - Cost: Higher
  - Uses document layout for better element classification
  
- **`fast`**: Rule-based extraction using traditional NLP
  - Best for: Simple text-heavy documents
  - Processing time: Fastest
  - Cost: Lowest
  - ⚠️ Not recommended for image-based files
  
- **`auto`**: Automatically selects the best strategy
  - Best for: Mixed document types, unknown formats
  - Processing time: Variable (optimized per document)
  - Cost: Optimized
  - Analyzes document characteristics to choose strategy
  
- **`ocr_only`**: Optical Character Recognition extraction
  - Best for: Scanned documents, images with text
  - Processing time: Moderate
  - Cost: Moderate
  - Model-based OCR for image files
  
- **`vlm`**: Vision Language Model (AI-powered)
  - Best for: Documents requiring visual understanding (charts, diagrams, infographics)
  - Processing time: Slower (AI processing)
  - Cost: Higher
  - Supported formats: `.bmp`, `.gif`, `.heic`, `.jpeg`, `.jpg`, `.pdf`, `.png`, `.tiff`, `.webp`
  - Uses advanced AI to understand visual context

**Success Response:**
```json
{
  "status": "success",
  "message": "File s3://bucket-name/folder/path/ processed successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

**⚠️ Important Note:** The workflow runs asynchronously. The API returns immediately after starting the job. Check the console logs or Unstructured platform for job status and results.

### Example Requests

**Default (hi_res) Strategy:**
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "s3://my-bucket/documents/",
    "awsK": "AKIAIOSFODNN7EXAMPLE",
    "awsS": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "unstrK": "your-unstructured-api-key",
    "supaK": "your-supabase-password"
  }'
```

**Fast Strategy (Quick Processing):**
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "s3://my-bucket/documents/",
    "awsK": "AKIAIOSFODNN7EXAMPLE",
    "awsS": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "unstrK": "your-unstructured-api-key",
    "supaK": "your-supabase-password",
    "strategy": "fast"
  }'
```

**VLM Strategy (AI Vision Understanding):**
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "s3://my-bucket/infographics/",
    "awsK": "AKIAIOSFODNN7EXAMPLE",
    "awsS": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "unstrK": "your-unstructured-api-key",
    "supaK": "your-supabase-password",
    "strategy": "vlm"
  }'
```

**OCR Strategy (Scanned Documents):**
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "s3://my-bucket/scanned-docs/",
    "awsK": "AKIAIOSFODNN7EXAMPLE",
    "awsS": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "unstrK": "your-unstructured-api-key",
    "supaK": "your-supabase-password",
    "strategy": "ocr_only"
  }'
```

### Render.com

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --worker-class=uvicorn.workers.UvicornWorker --workers=4 --timeout 240`
5. Add the required environment variables
6. Deploy!

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Yes |
| `UNSTRUCTURED_API_KEY` | Unstructured.io API key | Yes |
| `SUPABASE_DATABASE_URL` | PostgreSQL connection URL | Yes |
| `SUPABASE_PASSWORD` | PostgreSQL password | Yes |
| `PORT` | Port to run the server on | No (default: 8080) |
| `FLASK_ENV` | Environment (development/production) | No (default: production) |

## 📊 Project Structure

```
fastunstructapi/
├── main.py                    # Main application with workflow endpoint logic
├── wsgi.py                    # WSGI entry point for production
├── asgi.py                    # ASGI entry point (alternative)
├── requirements.txt           # Python dependencies (unstructured-client)
├── render.yaml                # Render deployment configuration
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables (not in git)
├── docs/                      # 📚 Documentation
│   ├── MIGRATION_SUMMARY.md   # Migration guide from partition endpoint
│   ├── README_UPDATE_SUMMARY.md  # README update changelog
│   ├── supabase-notes.txt     # Supabase integration notes
│   └── unstructured-notes.txt # Unstructured.io development notes
└── venv/                      # Virtual environment (not in git)
```

## 🔧 Troubleshooting

### Common Issues

**🔑 Authentication Errors**
- Verify your Unstructured API key at [platform.unstructured.io](https://platform.unstructured.io)
- Ensure the API key is passed correctly in the request
- Check that your API key has not expired

**☁️ S3 Connection Issues**
- Verify AWS credentials have read permissions on the S3 bucket
- Check the S3 path format: `s3://bucket-name/path/`
- Ensure the AWS region is accessible
- Verify bucket exists and is not empty

**🗄️ PostgreSQL Connection Issues**
- Verify Supabase password is correct
- Check if Supabase pooler endpoint is accessible
- Verify database name, username, and table exist
- Ensure table schema matches expected format

**📋 Job Not Completing**
- Jobs run asynchronously - they may take time to complete
- Check job status at [platform.unstructured.io](https://platform.unstructured.io)
- Review console logs for connector and workflow IDs
- Monitor Supabase database for incoming data

**🚀 Performance Issues**
- Use `fast` strategy for quicker processing of simple documents
- Use `auto` strategy to let Unstructured optimize automatically
- Use `hi_res` only for complex documents requiring high accuracy

**💾 Character Encoding Errors**
- Ensure your terminal supports UTF-8
- Set `PYTHONIOENCODING=utf-8` in your environment

## 📚 Supabase Database Schema

Your Supabase table should have this schema to receive processed data:

```sql
CREATE TABLE elements (
    id UUID PRIMARY KEY,
    record_id VARCHAR,
    element_id VARCHAR,
    text TEXT,
    embeddings DECIMAL[],
    parent_id VARCHAR,
    page_number INTEGER,
    is_continuation BOOLEAN,
    orig_elements TEXT,
    partitioner_type VARCHAR
);
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=main tests/
```

## 📚 Additional Resources

### Official Documentation
- **Unstructured Workflow Endpoint Docs**: [docs.unstructured.io/api-reference/workflow/overview](https://docs.unstructured.io/api-reference/workflow/overview)
- **Unstructured Platform**: [platform.unstructured.io](https://platform.unstructured.io)
- **API Key Management**: [platform.unstructured.io](https://platform.unstructured.io) → API Keys
- **PostgreSQL Destination**: [docs.unstructured.io/api-reference/workflow/destinations/postgresql](https://docs.unstructured.io/api-reference/workflow/destinations/postgresql)

### Project Documentation
- **Migration Guide**: [docs/MIGRATION_SUMMARY.md](docs/MIGRATION_SUMMARY.md) - Detailed migration information
- **README Update Notes**: [docs/README_UPDATE_SUMMARY.md](docs/README_UPDATE_SUMMARY.md) - Changelog for documentation
- **Supabase Integration**: [docs/supabase-notes.txt](docs/supabase-notes.txt) - Supabase setup and integration notes
- **Unstructured Notes**: [docs/unstructured-notes.txt](docs/unstructured-notes.txt) - Development notes and tips

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Unstructured.io](https://unstructured.io/) for the production-ready workflow endpoint
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Render](https://render.com/) for the hosting platform
- [Supabase](https://supabase.com/) for PostgreSQL hosting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Unstructured Workflow Endpoint** | [Documentation](https://docs.unstructured.io) | [Get API Key](https://platform.unstructured.io)