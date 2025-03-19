# WWLD (What Would Lebron Do?) - AI Eating Detection System

A Flask-based web application that uses computer vision and machine learning to detect eating behavior through webcam feed analysis. The system combines face mesh detection and hand tracking to identify when someone is eating.

## Features

- Real-time face mesh detection using MediaPipe
- Hand tracking and position analysis
- Eating behavior detection through mouth movement and hand position analysis
- Web-based interface for live video feed processing
- RESTful API endpoints for frontend communication

## Prerequisites

- Python 3.7+
- Webcam
- Modern web browser with JavaScript enabled

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wwld.git
cd wwld
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Dependencies

- Flask 2.0.1
- OpenCV 4.5.3.56
- NumPy 1.21.2
- MediaPipe 0.8.7.3

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Allow camera access when prompted by your browser.

4. The application will begin analyzing your webcam feed for eating behavior.

## Project Structure

```
wwld/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files (CSS, JS, images)
└── templates/         # HTML templates
```

## How It Works

The system uses a combination of computer vision techniques to detect eating behavior:

1. **Face Mesh Detection**: Tracks facial landmarks using MediaPipe to monitor mouth movement
2. **Hand Tracking**: Detects hand position relative to the face
3. **Eating Detection**: Analyzes mouth openness and hand position to determine if eating is occurring

## API Endpoints

- `GET /`: Serves the main application page
- `POST /process_frame`: Processes webcam frames for eating detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

I don't know what to put here this is a stupid project lol

## Acknowledgments

- MediaPipe team for the face and hand detection models
- Flask framework and its contributors
- OpenCV community for computer vision tools 