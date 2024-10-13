from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import base64
from config import AZURE_COMPUTER_VISION_ENDPOINT, AZURE_COMPUTER_VISION_KEY, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_NAME
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speechsdk

    
# Create a Flask app
app = Flask(__name__)
# Enable CORS for the Flask app
CORS(app)

# Initialize the AzureOpenAI client with your API key, version, and endpoint
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version='2024-02-01',
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)


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
    
    # Check if COMPUTER_VISION_ENDPOINT and COMPUTER_VISION_KEY are set
    if not AZURE_COMPUTER_VISION_ENDPOINT or not AZURE_COMPUTER_VISION_KEY:
        return jsonify({'error': 'Azure API credentials missing'}), 500

    # Prepare request headers for Azure Computer Vision API
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': AZURE_COMPUTER_VISION_KEY
    }
    
    # Analyze the image with Azure Computer Vision API
    api_url = f'{AZURE_COMPUTER_VISION_KEY}/vision/v3.2/analyze'
    params = {
        'visualFeatures': 'Tags',
        'language': 'en'
    }
    response = requests.post(api_url, headers=headers, params=params, data=file.read())

    # Check if the request was successful
    if response.status_code != 200:
        return jsonify({'error': 'Failed to analyze image'}), response.status_code

    # Parse the response
    data = response.json()
    # Extract tags from the response
    tags = [tag['name'] for tag in data.get('tags', [])]
    print("Tags for the image:", tags)

    # Define the messages for the chat completion
    messages = [
        {
            "role": "user",
            "content": f"""Given these image tags: {tags} (which are tags generated from an image of a flower plant, vegetable plant, or fruit plant) 
            ignore the tags that are of a more general nature (for example: flower, shrub, herb, plant, green, vegetable, etc.) and instead, 
            look for a tag that is the common name of a plant, vegetable, fruit, herb, or flower (for example: broccoli, tomato, lily, dandelion, etc.)  
            If there are multiple common name tags, (for example - lily and orchid) use the one that appears first in the list.  
            Write me a short detailed summary of the plant you've identified based on the tag, using less than 1000 characters.  
            Begin the response using the format 'The <plant name> (<latin name>) is a <rest of the response>.  
            Important: If the tags do not appear to be from an image of a plant, return 'There doesn't appear to be a plant in this image.  Upload an image of a plant or flower to identify.'  
            If none of the tags given are the common name for a plant, simply return 'Unable to identify plant based on the image.  
            Try using a picture of the plant flowering, fruiting, or at a different angle.'"""
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
    
    # Return plant information to the client
    return jsonify({'plant_info': response_text})

def synthesize_and_play_audio(plant_info):
    # Initialize speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config, audio_config=None)

    # Synthesize audio from plant information
    result = speech_synthesizer.speak_text_async(plant_info).get()
    
    # Check the result of the synthesis
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Successfully synthesized audio.")
        # Return the audio data directly as bytes
        return result.audio_data
    
    else:
        print("Text-to-speech synthesis failed.")
        return None

# Add the speech synthesis task as an asynchronous task after returning the plant information
@app.route('/synthesize_audio', methods=['POST'])
def synthesize_audio():
    plant_info = request.json.get('plant_info', '')
    # Call function to synthesize audio and get the audio data
    audio_data = synthesize_and_play_audio(plant_info)
    
    if audio_data is not None:
        # Convert audio data to a base64-encoded string
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Return the base64-encoded audio data in a JSON response
        return jsonify({'audio_data': audio_base64})
    
    else:
        # Return an error response if audio synthesis failed
        return jsonify({'error': 'Failed to synthesize audio.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)