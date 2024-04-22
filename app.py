from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from config import AZURE_ENDPOINT, AZURE_API_KEY
from config import AZURE_OPENAI_API_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME
from openai import AzureOpenAI

    
# Create a Flask app
app = Flask(__name__)
# Enable CORS for the Flask app
CORS(app)

# Initialize the AzureOpenAI client with your API key, version, and endpoint
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version='2024-02-01',
    azure_endpoint=os.getenv('AZURE_OPENAI_API_ENDPOINT') 
)

# Define the deployment name for the GPT-4 model
DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

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
        'visualFeatures': 'Tags',
        'language': 'en',
        'maxCandidates': '30'
    }

    response = requests.post(api_url, headers=headers, params=params, data=file.read())

    # Check if the request was successful
    if response.status_code != 200:
        return jsonify({'error': 'Failed to analyze image'}), response.status_code

    # Parse the response
    data = response.json()
    # Extract tags from the response
    #tags = data.get('tags', [])
    tags = [tag['name'] for tag in data.get('tags', [])]
    print("Tags for the image:", tags)

    # Define the messages for the chat completion
    messages = [
        {
            "role": "user",
            "content": f"Given these tags: {tags}, - (which are tags that refer to an image of a flower plant, vegetable plant, or fruit plant) - ignore the tags that are of a more general nature (flower, shrub, herb, plant, green, vegetable, etc.) and instead, look for a tag that is the common name of a plant, vegetable, fruit, herb, or flower (for example - broccoli, tomato, lily, dandelion, etc.)  If there are multiple common name tags, (for example - lily and orchid) use the one that appears first in the list.  Write me a short detailed summary of the plant you've identified based on the tag, using less than 1000 characters.  Begin the response using the format 'The <plant name> (<latin name>) is a <rest of the response>.  If none of the tags given are the common name for a plant, simply return 'Unable to identify plant based on the image.  Try using a picture of the plant flowering, fruiting, or at a different angle.'"
        }
    ]

    # Send a chat completion request using the AzureOpenAI client
    print('Sending a message to GPT4')

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT_NAME, 
        messages=messages,
        max_tokens=200
    )

    # Retrieve the response text from the GPT-4 model
    response_text = response.choices[0].message.content

    # Print the information to the console for debugging purposes
    print('Plant Information:', response_text)
    
    # Return the information as a JSON response
    return jsonify({'plant_info': response_text})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)