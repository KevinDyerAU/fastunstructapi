"""
Integration tests for FastUnstructAPI with the new Unstructured Workflow Client.

This script tests the key functionality of the updated API, including:
- Document processing from S3
- Single file processing
- Error handling
"""

import os
import sys
import json
import unittest
import requests
from dotenv import load_dotenv
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

class TestFastUnstructAPI(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_url = os.getenv('TEST_API_URL', 'http://localhost:8080')
        cls.test_file = os.getenv('TEST_S3_FILE', 's3://your-test-bucket/test-document.pdf')
        cls.test_folder = os.getenv('TEST_S3_FOLDER', 's3://your-test-bucket/test-folder/')
        
        # Verify required environment variables
        assert os.getenv('AWS_ACCESS_KEY_ID'), "AWS_ACCESS_KEY_ID is required"
        assert os.getenv('AWS_SECRET_ACCESS_KEY'), "AWS_SECRET_ACCESS_KEY is required"
        assert os.getenv('UNSTRUCTURED_API_KEY'), "UNSTRUCTURED_API_KEY is required"
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"].lower(), "fastunstructapi is running")
    
    def test_process_single_file(self):
        """Test processing a single file from S3"""
        payload = {
            "s3Path": self.test_file,
            "awsK": os.getenv('AWS_ACCESS_KEY_ID'),
            "awsS": os.getenv('AWS_SECRET_ACCESS_KEY'),
            "unstrK": os.getenv('UNSTRUCTURED_API_KEY'),
            "strategy": "hi_res"
        }
        
        response = requests.post(
            f"{self.base_url}/process/single",
            json=payload,
            timeout=300  # 5 minute timeout for processing
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("message", result)
        self.assertIn("elements", result)
        self.assertIn("metadata", result)
        self.assertGreater(len(result["elements"]), 0, "No elements were extracted from the document")
    
    def test_process_documents(self):
        """Test processing multiple documents from an S3 folder"""
        payload = {
            "folder": self.test_folder,
            "strategy": "hi_res"
        }
        
        response = requests.post(
            f"{self.base_url}/process",
            json=payload,
            timeout=600  # 10 minute timeout for batch processing
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("message", result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "completed")
        self.assertIn("workflow_id", result)
        self.assertIn("run_id", result)
    
    def test_invalid_credentials(self):
        """Test error handling for invalid credentials"""
        payload = {
            "s3Path": self.test_file,
            "awsK": "invalid_key",
            "awsS": "invalid_secret",
            "unstrK": "invalid_api_key",
            "strategy": "hi_res"
        }
        
        response = requests.post(
            f"{self.base_url}/process/single",
            json=payload,
            timeout=60
        )
        
        # Should return 400 or 500 with error message
        self.assertIn(response.status_code, [400, 500])
        result = response.json()
        self.assertIn("error", result or {})


if __name__ == "__main__":
    # Run tests with increased verbosity
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)
