from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from config import AZURE_ENDPOINT, AZURE_API_KEY

# Create Flask app
app = Flask(__name__)

# Enable CORS for the Flask app
CORS(app)


# Azure Computer Vision API credentials
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_API_KEY = os.getenv('AZURE_API_KEY')


@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Testing: Image Received from Frontend.
    print("Image received by the backend")
    
    

    # --------------------------- START AZURE ---------------------- #
    
    # Check if AZURE_ENDPOINT and AZURE_API_KEY are set
    if not AZURE_ENDPOINT or not AZURE_API_KEY:
        return jsonify({'error': 'Azure API credentials missing'}), 500
    
    # Prepare the request headers
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': AZURE_API_KEY
    }

    # Send the image to Azure Computer Vision API
    api_url = f'{AZURE_ENDPOINT}/vision/v3.2/analyze'
    params = {
        'visualFeatures': 'Categories,Tags,Objects,Color',
        'language': 'en',
        'maxCandidates': 3
    }

    response = requests.post(api_url, headers=headers, params=params, data=file.read())

    # Check if the request was successful
    if response.status_code != 200:
        return jsonify({'error': 'Failed to analyze image'}), response.status_code

    # Parse the response
    data = response.json()
    # Extract information from the response
    categories = data.get('categories', [])
    tags = data.get('tags', [])
    objects = data.get('objects', [])
    color = data.get('color', {})
    # Extract the description (captions)
    description_data = data.get('description', {}).get('captions', [])
    description = description_data[0].get('text', 'No description available') if description_data else 'No description available'

    # Create a dictionary containing the analysis results
    analysis_results = {
        'description': description,
        'categories': [category['name'] for category in categories],
        'tags': [tag['name'] for tag in tags],
        'objects': [obj['object'] for obj in objects],
        'color': color.get('dominantColors', [])
    }

    # Return the analysis results as JSON
    return jsonify(analysis_results), 200

    # --------------------------- END AZURE ---------------------- #
    
    
    

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)