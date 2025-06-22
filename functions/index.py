import json
import os
from flask import Flask, request
from main import app as flask_app
from wsgi import application as wsgi_app

# Initialize Flask app
app = Flask(__name__)

# Netlify functions use a different event structure
# We need to adapt the Netlify event to a Flask request
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def handler(path):
    # Get the Netlify event
    event = request.environ.get('lambda.event', {})
    
    # Convert Netlify event to Flask request
    flask_request = request.environ
    
    # Create a Flask response
    with flask_app.test_request_context(path, method=event.get('httpMethod', 'GET')):
        flask_request = flask_app.test_client().open(
            path=path,
            method=event.get('httpMethod', 'GET'),
            headers=event.get('headers', {}),
            data=event.get('body', '')
        )
        
        # Get the Flask response
        response = flask_app.full_dispatch_request()
        
        # Convert Flask response to Netlify response
        netlify_response = {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
        
        return netlify_response

# Export the function for Netlify
handler = app.route("/")(handler)
