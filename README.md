# AI Plant Identifier

## Overview

This project is a web application that allows users to upload images of plants or flowers to be identified. Utilizing Azure's Computer Vision and OpenAI's large language model, the application analyzes the uploaded images and provides detailed information about the identified plants. The application also synthesizes audio descriptions of the plants for a multi-modal user experience.

## Features

- **Image Upload**: Users can upload images of plants or flowers for analysis.
- **Plant Identification**: The application uses Azure's Computer Vision API to analyze the image and extract relevant tags.
- **Detailed Descriptions**: Based on the identified tags, the application generates a detailed summary of the plant using OpenAI's large language model.
- **Audio Synthesis**: The application synthesizes audio descriptions of the identified plants, allowing users an alternative way to consume the information.

## Installation

To set up the project, ensure you have Python installed on your machine. Then, follow these steps:

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   - On Windows (using Command Prompt):
     ```bash
     .venv\Scripts\activate
     ```
   - On Windows (using Git Bash):
     ```bash
     source .venv/Scripts/activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `config.py` file in the root directory and add your Azure API keys:

   ```python
   AZURE_COMPUTER_VISION_ENDPOINT = 'your_computer_vision_endpoint'
   AZURE_COMPUTER_VISION_KEY = 'your_computer_vision_key'
   AZURE_OPENAI_ENDPOINT = 'your_openai_endpoint'
   AZURE_OPENAI_KEY = 'your_openai_key'
   AZURE_OPENAI_DEPLOYMENT_NAME = 'your_openai_deployment_name'
   AZURE_SPEECH_KEY = 'your_speech_key'
   AZURE_SPEECH_REGION = 'your_speech_region'
   ```

## Usage

1. Run the Flask application:

   ```bash
   python app.py
   ```

2. Locate the `index.html` file in the project directory and open it in your preferred web browser.

3. Upload an image of a plant or flower to identify.

4. View the analysis results and either read or listen to the description of the plant.

## File Descriptions

- **app.py**: The server-side code containing the Flask API for handling image uploads, plant identification, and audio synthesis.
- **config.py**: Configuration file containing the environment variables such as API keys and endpoints for Azure services.
- **functions.js**: JavaScript file managing the front-end interactions, including file uploads and audio playback.
- **index.html**: The main HTML file serving as the front-end of the web application.

## Dependencies

- **Flask**: For building the web application and handling HTTP requests.
- **Flask-CORS**: For enabling Cross-Origin Resource Sharing in the Flask app.
- **Requests**: For making HTTP requests to Azure APIs.
- **OpenAI**: For AI-generated plant descriptions.
- **Azure Cognitive Services**: For image analysis and speech synthesis.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.
