"""ASGI entry point for the FastUnstruct API."""
import os
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from main import create_app

# Create Flask app
flask_app = create_app()

# Create FastAPI app that wraps the Flask app
app = FastAPI()

# Mount the Flask app at the root
app.mount("/", WSGIMiddleware(flask_app))

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
