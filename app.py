"""
WWLD (What Would Lebron Do?) - Flask Server Application

This is the main server application for the WWLD AI eating detection system.
The application uses computer vision and machine learning to detect eating behavior
through webcam feed analysis.

Key Components:
1. Face Mesh Detection - Uses MediaPipe to track facial landmarks
2. Hand Tracking - Detects hand position relative to mouth
3. Eating Detection - Combines mouth movement and hand position analysis
4. Web Server - Provides endpoints for the frontend application

Dependencies:
- Flask: Web framework
- OpenCV: Computer vision operations
- MediaPipe: ML-powered face and hand detection
- NumPy: Numerical computations
- Base64: Image data encoding/decoding

Author: Your Smart Eating Detection Assistant Team
"""

from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import mediapipe as mp
from collections import deque
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize MediaPipe Face Mesh with optimized parameters for eating detection
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.3,  # Decreased for better sensitivity
    min_tracking_confidence=0.3    # Decreased for better tracking
)

# Initialize hand tracking with optimized parameters
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.3,  # Decreased for better sensitivity
    min_tracking_confidence=0.3    # Decreased for better tracking
)

# Configuration for eating detection
mouth_openness_history = deque(maxlen=10)  # Tracks mouth movement over time
HAND_TO_MOUTH_THRESHOLD = 0.7  # Distance threshold for hand-to-mouth proximity
MOUTH_OPEN_THRESHOLD = 0.01    # Threshold for detecting open mouth

def calculate_mouth_openness(face_landmarks):
    """
    Calculate the degree of mouth openness using facial landmarks.
    
    Args:
        face_landmarks: MediaPipe face landmarks object
        
    Returns:
        float: A measure of mouth openness (larger value = more open)
    """
    # Using more accurate mouth landmarks for better detection
    upper_inner_lip = face_landmarks.landmark[13]  # Upper inner lip
    lower_inner_lip = face_landmarks.landmark[14]  # Lower inner lip
    upper_outer_lip = face_landmarks.landmark[0]   # Upper outer lip
    lower_outer_lip = face_landmarks.landmark[17]  # Lower outer lip
    
    # Calculate both inner and outer mouth openness
    inner_mouth_openness = abs(lower_inner_lip.y - upper_inner_lip.y)
    outer_mouth_openness = abs(lower_outer_lip.y - upper_outer_lip.y)
    
    # Use the larger of the two values for more reliable detection
    mouth_openness = max(inner_mouth_openness, outer_mouth_openness)
    print(f"Inner mouth openness: {inner_mouth_openness}")
    print(f"Outer mouth openness: {outer_mouth_openness}")
    print(f"Final mouth openness: {mouth_openness}")
    return mouth_openness

def is_hand_near_mouth(face_landmarks, hand_landmarks):
    """
    Determine if a hand is near the mouth region.
    
    Args:
        face_landmarks: MediaPipe face landmarks object
        hand_landmarks: MediaPipe hand landmarks object
        
    Returns:
        bool: True if hand is near mouth, False otherwise
    """
    if not face_landmarks or not hand_landmarks:
        return False
    
    # Define mouth region using key facial landmarks
    mouth_points = [
        face_landmarks.landmark[13],  # Upper inner lip
        face_landmarks.landmark[14],  # Lower inner lip
        face_landmarks.landmark[78],  # Left mouth corner
        face_landmarks.landmark[308]  # Right mouth corner
    ]
    
    # Calculate mouth region center
    mouth_center_x = sum(point.x for point in mouth_points) / len(mouth_points)
    mouth_center_y = sum(point.y for point in mouth_points) / len(mouth_points)
    
    # Check all hand landmarks for proximity to mouth
    for i in range(21):  # MediaPipe hands has 21 landmarks
        hand_point = hand_landmarks.landmark[i]
        distance = np.sqrt(
            (mouth_center_x - hand_point.x)**2 + 
            (mouth_center_y - hand_point.y)**2
        )
        if distance < HAND_TO_MOUTH_THRESHOLD:
            print(f"Hand point {i} distance to mouth: {distance}")
            return True
    
    return False

def detect_eating(frame):
    """
    Detect eating behavior in a video frame using face and hand tracking.
    
    Args:
        frame: numpy.ndarray, BGR format frame from video feed
        
    Returns:
        bool: True if eating behavior is detected, False otherwise
    """
    # Convert BGR to RGB for MediaPipe processing
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process face mesh
    face_results = face_mesh.process(frame_rgb)
    if not face_results.multi_face_landmarks:
        print("No face detected")
        return False
    
    # Process hands
    hand_results = hands.process(frame_rgb)
    
    # Get the first face detected
    face_landmarks = face_results.multi_face_landmarks[0]
    
    # Calculate and track mouth openness
    mouth_openness = calculate_mouth_openness(face_landmarks)
    mouth_openness_history.append(mouth_openness)
    
    # Check for hand proximity to mouth
    hand_near_mouth = False
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            if is_hand_near_mouth(face_landmarks, hand_landmarks):
                hand_near_mouth = True
                break
    else:
        print("No hands detected")
    
    # Calculate detection metrics
    avg_mouth_openness = sum(mouth_openness_history) / len(mouth_openness_history)
    mouth_movement = max(mouth_openness_history) - min(mouth_openness_history)
    
    print(f"Average mouth openness: {avg_mouth_openness}")
    print(f"Mouth movement: {mouth_movement}")
    print(f"Hand near mouth: {hand_near_mouth}")
    
    # Determine if eating is detected based on combined criteria
    eating_detected = (
        (avg_mouth_openness > MOUTH_OPEN_THRESHOLD or mouth_movement > 0.005) and
        hand_near_mouth
    )
    
    print(f"Eating detected: {eating_detected}")
    return eating_detected

@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """
    Process a video frame for eating detection.
    
    Expects a JSON payload with a base64-encoded image.
    Returns JSON with eating detection result.
    """
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    eating_detected = detect_eating(frame)
    return jsonify({'eatingDetected': eating_detected})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
