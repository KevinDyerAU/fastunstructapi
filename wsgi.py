import os
import sys
import pathlib

# Add project root to Python path
project_root = str(pathlib.Path(__file__).parent.parent)  # Move up one level to include src/
sys.path.append(project_root)

from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)