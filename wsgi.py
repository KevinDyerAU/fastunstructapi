import os
import sys
import pathlib

# Add project root and src directory to Python path
project_root = str(pathlib.Path(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)