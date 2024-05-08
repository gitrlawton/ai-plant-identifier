// Define DOM elements
const fileInput = document.getElementById('file-input');
const chooseFileButton = document.getElementById('choose-file-btn');
const uploadButton = document.getElementById('upload-btn');
const imagePreview = document.getElementById('image-preview');
const previewImage = document.getElementById('preview-img');
const descriptionElement = document.getElementById('description');
const infoContainer = document.getElementById('info-container');
const statusElement = document.getElementById('status');
const audioControls = document.getElementById('audio-controls'); // Audio controls container
const audioPlayer = document.getElementById('audio-player'); // Audio player

let plantInfo = ''; // Variable to store plant information

// Event listener for file input button
chooseFileButton.addEventListener('click', function () {
    fileInput.click();
});

// Event listener for file selection
fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function () {
            previewImage.src = reader.result;
            imagePreview.style.display = 'block';
            uploadButton.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

// Event listener for upload button
uploadButton.addEventListener('click', function () {
    const file = fileInput.files[0];
    
    // Disable the Choose File button to prevent further selections during the process
    chooseFileButton.disabled = true;
    
    uploadImage(file);
    
    // Hide plant information and audio controls
    infoContainer.style.display = 'none';
    audioControls.style.display = 'none';

    // Hide the upload button after it's clicked
    uploadButton.style.display = 'none';
});

// Function to upload the image and handle the response
function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Update status element
    statusElement.innerText = "Uploading image...";
    statusElement.style.display = 'block';

    fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to upload image.');
        }

        return response.json();
    })
    .then(data => {
        // Save plant information to a variable
        plantInfo = data.plant_info;
        
        statusElement.innerText = "Analyzing image...";

        // Start audio synthesis
        return synthesizeAudio(plantInfo);
    })
    .then(() => {
        // Re-enable the Choose File button at the end of the promise chain
        chooseFileButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        statusElement.innerText = "An error occurred during the upload. Please try again.";
        
        // Re-enable the Choose File button in case of error
        chooseFileButton.disabled = false;
    });
}

// Function to synthesize audio and set it to the audio player
function synthesizeAudio(plantInfo) {
    return fetch('http://localhost:5000/synthesize_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'plant_info': plantInfo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.audio_data) {
            // Convert base64-encoded audio data to a Blob
            const audioBlob = new Blob([Uint8Array.from(atob(data.audio_data), c => c.charCodeAt(0))], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);

            // Set the audio source
            audioPlayer.src = audioUrl;

            // Update the description element with the plant information
            descriptionElement.innerHTML = `${plantInfo || 'No information available'}`;

            // Show the plant information container
            infoContainer.style.display = 'block';

            // Hide the status element as the process has completed
            statusElement.style.display = 'none';
            statusElement.innerText = '';

            // Show the audio controls only after successfully setting the audio source
            audioControls.style.display = 'block';
        } else {
            console.error('No audio data received');
        }
    })
    .catch(error => {
        console.error('Error fetching or playing audio:', error);
        statusElement.innerText = "An error occurred during the process. Please try again.";
    });
}