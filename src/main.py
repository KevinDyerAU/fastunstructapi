"""
Main entry point for FastUnstructAPI

This module contains the Flask application and API endpoints for document processing.
"""

from typing import Dict, Any
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pydantic_spec import FlaskPydanticSpec, Response
from pydantic import BaseModel
from .pipeline import process_documents
from .config import get_config


logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)
spec = FlaskPydanticSpec("FastUnstructAPI", title="FastUnstructAPI")
spec.register(app)


class FileProcessRequest(BaseModel):
    """Request model for processing documents"""
    folder: str
    strategy: str = "hi_res"


class FileAccessRequest(BaseModel):
    """Request model for accessing documents with explicit credentials"""
    fileName: str
    awsK: str
    awsS: str
    unstrK: str
    supaK: str
    strategy: str = "hi_res"


class SingleFileRequest(BaseModel):
    """Request model for processing a single file from S3"""
    s3Path: str
    awsK: str
    awsS: str
    unstrK: str
    strategy: str = "hi_res"


class SingleFileResponse(BaseModel):
    """Response model for single file processing"""
    message: str
    file: str
    elements: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class ProcessingResponse(BaseModel):
    """Response model for processing operations"""
    message: str
    folder: Optional[str] = None


@app.route("/")
def root():
    """Health check endpoint"""
    return jsonify({"message": "FastUnstructAPI is running"})


@app.route("/process", methods=["POST"])
@spec.validate(
    body=Response(HTTP_200=ProcessingResponse, HTTP_400=ProcessingResponse)
)
def process():
    """Process documents from S3 using configured credentials"""
    try:
        data = request.get_json()
        folder = data.get("folder")
        strategy = data.get("strategy", "hi_res")
        
        if not folder:
            return jsonify({"message": "Folder path is required"}), 400
            
        result = process_documents(folder, strategy=strategy)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        return jsonify({"message": f"Error processing documents: {str(e)}"}), 500


@app.route("/access", methods=["POST"])
@spec.validate(
    body=Response(HTTP_200=ProcessingResponse, HTTP_400=ProcessingResponse)
)
async def access():
    """Process documents with explicit credentials"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "Request body is required"}), 400
            
        result = process_documents(
            folder=data["fileName"],
            aws_config={"key": data["awsK"], "secret": data["awsS"]},
            unstructured_config={"api_key": data["unstrK"]},
            supabase_config={"password": data["supaK"]},
            strategy=data.get("strategy", "hi_res")
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error accessing documents: {str(e)}")
        return jsonify({"message": f"Error accessing documents: {str(e)}"}), 500


@app.route("/process_single", methods=["POST"])
@spec.validate(
    body=Response(HTTP_200=SingleFileResponse, HTTP_400=SingleFileResponse)
)
async def process_single():
    """Process a single file from S3"""
    try:
        data = request.get_json()
        
        if not data or not data.get("s3Path"):
            return jsonify({"message": "S3 path is required"}), 400
            
        result = process_single_file(
            s3_path=data["s3Path"],
            aws_config={"key": data["awsK"], "secret": data["awsS"]},
            unstructured_config={"api_key": data["unstrK"]},
            strategy=data.get("strategy", "hi_res")
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing single file: {str(e)}")
        return jsonify({"message": f"Error processing single file: {str(e)}"}), 500


if __name__ == "__main__":
    config = get_config()
    app.run(debug=config.debug, host="0.0.0.0", port=8080)
