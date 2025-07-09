# FastUnstruct API

A high-performance FastAPI-wrapped Flask application for processing and extracting structured data from documents using Unstructured.io, with seamless S3 and PostgreSQL integration. Deployable to Render with zero configuration.

## ✨ Features

- **Document Processing**: Extract structured data from various document formats
- **S3 Integration**: Directly process documents from AWS S3 buckets
- **PostgreSQL Storage**: Store and query processed data efficiently
- **RESTful API**: Simple and intuitive API endpoints
- **Production Ready**: ASGI server with Uvicorn for high performance
- **Health Checks**: Built-in health check endpoint for monitoring
- **One-Click Deployment**: Deploy to Render with a single click
- **Scalable**: Built with production deployment in mind

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- AWS credentials (for S3 access)
- Unstructured.io API key
- PostgreSQL database (local or Supabase)

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

### Process a Document

```http
POST /process
Content-Type: application/json

{
  "fileName": "path/to/document.pdf",
  "awsK": "your_aws_key",
  "awsS": "your_aws_secret",
  "unstrK": "your_unstructured_key",
  "supaK": "your_supabase_key"
}
```

### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "ok"
}
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

## 🔧 Troubleshooting

### Common Issues

1. **Character Encoding Errors**
   - Ensure your terminal supports UTF-8
   - Set `PYTHONIOENCODING=utf-8` in your environment

2. **S3 Connection Issues**
   - Verify your AWS credentials
   - Check S3 bucket permissions

3. **PostgreSQL Connection Issues**
   - Verify database credentials
   - Check if the database is accessible from your network

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Unstructured.io](https://unstructured.io/) for the amazing document processing library
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Render](https://render.com/) for the hosting platform

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_APP=main.py
FLASK_ENV=development
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
UNSTRUCTURED_API_KEY=your_unstructured_key
POSTGRES_PASSWORD=your_postgres_password
```

### 5. Run the application

```bash
# Development server
python main.py

# Or using Gunicorn for production-like environment
gunicorn wsgi:app
```

The API will be available at `http://localhost:8080`

## API Endpoints

### Process a file

```http
POST /process
Content-Type: application/json

{
  "fileName": "path/to/your/file.pdf",
  "awsK": "your_aws_key",
  "awsS": "your_aws_secret",
  "unstrK": "your_unstructured_key",
  "supaK": "your_supabase_key"
}
```

### Check API status

```http
GET /
```

## Deployment to Render

### 1. Create a new Web Service

1. Go to your Render dashboard and click "New +" then select "Web Service"
2. Connect your Git repository

### 2. Configure the service

- **Name**: fastunstructapi (or your preferred name)
- **Region**: Choose the closest region to your users
- **Branch**: main (or your preferred branch)
- **Root Directory**: / (root of the repository)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`

### 3. Set up environment variables

Add the following environment variables in the Render dashboard:

- `FLASK_APP=main.py`
- `FLASK_ENV=production`
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `UNSTRUCTURED_API_KEY`: Your Unstructured.io API key
- `POSTGRES_PASSWORD`: Your PostgreSQL password

### 4. Deploy

Click "Create Web Service" to deploy your application.

## Project Structure

```
fastunstructapi/
├── main.py           # Main application code
├── wsgi.py          # WSGI entry point for production
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## License

MIT