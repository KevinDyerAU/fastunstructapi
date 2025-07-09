from main import create_app
import os

app = create_app()

if __name__ == "__main__":
    # This block is for local testing with `python wsgi.py`
    # In production, the WSGI server will import the app directly
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)