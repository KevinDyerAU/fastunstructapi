import os
import sys
import pathlib

# Add src directory to Python path
src_path = str(pathlib.Path(__file__).parent / 'src')
sys.path.append(src_path)

from main import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)