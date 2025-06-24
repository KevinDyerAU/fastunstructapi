import os
import sys
import pathlib

# Get the absolute path to the project root
project_root = str(pathlib.Path(__file__).parent)
src_dir = os.path.join(project_root, 'src')

# Add src directory to Python path
sys.path.append(src_dir)

from src.main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)