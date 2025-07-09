from main import create_app
import os
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Create Flask app
flask_app = create_app()

# Create FastAPI app that wraps the Flask app
app = FastAPI()
app.mount("/", WSGIMiddleware(flask_app))

# This is needed for Render's health checks
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)