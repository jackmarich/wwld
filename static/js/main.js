/**
 * WWLD (What Would Lebron Do?) - Main Application Logic
 * 
 * This script handles the core functionality of the WWLD application:
 * 1. Webcam access and management
 * 2. Frame capture and processing
 * 3. Server communication for eating detection
 * 4. Video transition management
 * 
 * The application works by:
 * - Capturing frames from the webcam every second
 * - Sending frames to the server for AI processing
 * - Showing a motivational video when eating is detected
 * 
 * @requires MediaDevices API
 * @requires Canvas API
 * @requires Fetch API
 */

/**
 * Initialize webcam access and set up video stream
 * Handles errors and updates UI accordingly
 */
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        const video = document.getElementById('video');
        video.srcObject = stream;
        video.play().catch(err => console.error("Error playing video:", err));
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
        document.querySelector('.status-indicator span').textContent = 'Camera Error';
        document.querySelector('.status-dot').style.backgroundColor = '#ef4444';
    });

/**
 * Captures a frame from the webcam and sends it to the server for processing
 * Handles the response and triggers the motivational video if eating is detected
 */
function captureFrame() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    // Set canvas size to match video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame onto the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to a base64-encoded image
    const imageData = canvas.toDataURL('image/jpeg');

    // Send the image to the server for processing
    fetch('/process_frame', {
        method: 'POST',
        body: JSON.stringify({ image: imageData }),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            if (data.eatingDetected) {
                const videoElem = document.getElementById('motivationVideo');
                const videoContainer = document.querySelector('.video-container');
                const motivationContainer = document.querySelector('.motivation-container');

                // If the video is not already visible, show and play it
                if (!videoElem.classList.contains('show')) {
                    // Fade out the webcam feed
                    videoContainer.style.opacity = '0';

                    // After the fade out, show and play the motivation video
                    setTimeout(() => {
                        videoContainer.style.display = 'none';
                        videoElem.classList.add('show');
                        motivationContainer.style.display = 'block';
                        videoElem.play()
                            .then(() => console.log('Video started playing successfully'))
                            .catch(error => console.error('Error playing video:', error));

                        // When the motivation video ends, show the webcam feed again
                        videoElem.onended = () => {
                            videoElem.classList.remove('show');
                            motivationContainer.style.display = 'none';
                            videoContainer.style.display = 'block';
                            setTimeout(() => {
                                videoContainer.style.opacity = '1';
                            }, 50);
                        };
                    }, 300);
                }
            }
        })
        .catch(error => console.error('Error processing frame:', error));
}

// Start the frame capture loop
setInterval(captureFrame, 1000);
