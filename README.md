# FastAPI Image Classifier, Sentiment Analyzer, and Chat AI

A modern FastAPI application that performs image classification using ResNet-18, sentiment analysis using transformers, and offers a conversational AI chat interface with image understanding powered by SmolVLM-Instruct. Complete with a beautiful and responsive web interface.

## Features

- **🖼️ Image Classification**: Upload images for real-time classification using ResNet-18.
- **💭 Sentiment Analysis**: Analyze text sentiment using transformer models.
- **🤖 Conversational Chat AI**: Engage in multimodal conversations with an AI that understands both text and images (powered by SmolVLM-Instruct). Supports conversation history and session management.
- **🌐 Web Interface**: Modern, responsive frontend with drag-and-drop functionality for images and interactive chat.
- **📊 Interactive Results**: Visual confidence scores for classification and clear sentiment indicators.
- **⚡ Real-time Processing**: Fast inference with PyTorch and transformers.
- **📱 Mobile Friendly**: Responsive design that works on all devices.

## Quick Start

### 1. Setup Virtual Environment & Install Dependencies

It's recommended to use a virtual environment. The preferred name for this project is `fastapi_env`.

```bash
# Create a virtual environment (if you don't have one yet)
# On Windows:
# python -m venv fastapi_env
# On Linux/Mac:
# python3 -m venv fastapi_env

# Activate the virtual environment:
# On Windows:
fastapi_env\Scripts\activate
# On Linux/Mac:
source fastapi_env/bin/activate

# Install Python packages
pip install -r requirements.txt
```
*Note: If you encounter issues with PyTorch/CUDA, especially for the ML models, please refer to the [official PyTorch installation guide](https://pytorch.org/get-started/locally/) for instructions tailored to your system.*

### 2. Run the Server

Once the environment is activated and dependencies are installed:

```bash
python server.py
```

The server will start on `http://localhost:8002`.
You should see output indicating that the models are loading, for example:
`INFO:     Started server process [xxxxx]`
`INFO:     Waiting for application startup.`
`INFO:     Application startup complete.`
`INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)`
`Using device: cpu` (or `cuda` if available)
`Initializing chat models...`
`✓ SmolVLM-Instruct loaded successfully for chat using pipeline...`

### 3. Access the Application

- **🌐 Web Interface (Recommended)**: Open [http://localhost:8002](http://localhost:8002) in your browser.
  - Features a modern, user-friendly UI for all functionalities including image classification, sentiment analysis, and chat.
- **📚 API Documentation (Swagger UI)**: Open [http://localhost:8002/docs](http://localhost:8002/docs) in your browser.
  - Allows you to interactively explore and test all API endpoints.

## API Endpoints

All API endpoints are accessible via the base URL `http://localhost:8002`.

### GET `/`
Serves the main web interface (`static/index.html`).

### GET `/health`
A health check endpoint.
- **Response**: JSON object indicating server status.
  ```json
  {
    "msg": "Up and running!  Visit /docs for Swagger UI."
  }
  ```

### POST `/predict`
Accepts an image file and returns the predicted class label and confidence score.
- **Request**: Multipart form data with a `file` (JPEG or PNG).
- **Response**: JSON with filename, predicted class, and confidence.
  ```json
  {
    "filename": "dog.jpg",
    "predicted_class": "golden_retriever",
    "confidence": 0.8234
  }
  ```

### GET `/sentiment_analysis`
Analyzes the sentiment of a provided text string.
- **Query Parameter**: `text` (string).
- **Response**: JSON with the original text and sentiment analysis result (label and score).
  ```json
  {
    "text": "I love this application!",
    "sentiment": {
      "label": "POSITIVE",
      "score": 0.9998
    }
  }
  ```

### POST `/chat`
Engages in a multimodal conversation. Accepts text and an optional image, supports session management for conversation history.
- **Request**: Multipart form data:
    - `message` (str, required): The user's text message.
    - `image` (UploadFile, optional): An image file (JPEG/PNG).
    - `session_id` (str, optional): Session ID for continuing an existing conversation. If omitted, a new session is created.
- **Response**: JSON with the user's message, assistant's response, and session details.
  ```json
  {
    "message": "What do you see in this image?",
    "response": "I see a landscape with mountains and a lake.",
    "has_image": true,
    "model_used": "SmolVLM-Instruct",
    "session_id": "your-session-id",
    "conversation_length": 2
  }
  ```

### GET `/chat/history/{session_id}`
Retrieves the conversation history for a specific session.
- **Path Parameter**: `session_id` (str, required).
- **Response**: JSON with session ID, full conversation history, and length.
  ```json
  {
    "session_id": "your-session-id",
    "history": [
      {
        "role": "user",
        "content": [{"type": "image"}, {"type": "text", "text": "What do you see?"}],
        "timestamp": "2025-01-01T12:00:00.000Z"
      },
      {
        "role": "assistant",
        "content": [{"type": "text", "text": "I see a landscape..."}],
        "timestamp": "2025-01-01T12:00:01.000Z"
      }
    ],
    "length": 2
  }
  ```

### DELETE `/chat/history/{session_id}`
Clears the conversation history for a specific session.
- **Path Parameter**: `session_id` (str, required).
- **Response**: JSON confirming clearance.
  ```json
  {
    "message": "Conversation history cleared for session your-session-id"
  }
  ```

### GET `/chat/sessions`
Lists all active conversation sessions.
- **Response**: JSON with a list of active sessions, their message counts, and last update times.
  ```json
  {
    "active_sessions": [
      {
        "session_id": "session-1-id",
        "message_count": 4,
        "last_updated": "2025-01-01T12:05:00.000Z"
      }
    ],
    "total_sessions": 1
  }
  ```

## Usage Examples (API via `curl`)

These examples demonstrate how to interact with the API endpoints using `curl`. Ensure the server is running (`python server.py`) before trying these.

### Image Classification

**Upload an image for classification:**
```bash
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8002/predict
```
*(Replace `/path/to/your/image.jpg` with the actual path to an image file, e.g., `cat.jpg` or `dog.png`)*

### Sentiment Analysis

**Analyze sentiment of a text string:**
```bash
curl -X GET "http://localhost:8002/sentiment_analysis?text=I%20love%20this%20amazing%20application!"
```

### Conversational Chat AI

**1. Start a new chat conversation (text only):**
```bash
curl -X POST -F "message=Hello, how are you today?" http://localhost:8002/chat
```
*Take note of the `session_id` returned in the response. You'll use it to continue the conversation.*

**2. Continue the conversation with the `session_id`:**
```bash
curl -X POST -F "message=What can you do?" -F "session_id=your-session-id" http://localhost:8002/chat
```
*(Replace `your-session-id` with the actual ID from the previous response.)*

**3. Send an image with a question in a new or existing session:**
```bash
curl -X POST \
  -F "message=What do you see in this image?" \
  -F "image=@/path/to/your/photo.jpg" \
  -F "session_id=your-session-id" \
  http://localhost:8002/chat
```
*(Replace `/path/to/your/photo.jpg` with an actual image file path. If `session_id` is omitted, a new session will be started.)*

**4. Ask a follow-up question about the previously sent image:**
*(Ensure you use the correct `session_id` where the image was uploaded)*
```bash
curl -X POST \
  -F "message=Can you tell me more about the main subject in the image?" \
  -F "session_id=your-session-id" \
  http://localhost:8002/chat
```

### Managing Chat History

**1. Get conversation history for a session:**
```bash
curl -X GET http://localhost:8002/chat/history/your-session-id
```

**2. List all active chat sessions:**
```bash
curl -X GET http://localhost:8002/chat/sessions
```

**3. Clear conversation history for a specific session:**
```bash
curl -X DELETE http://localhost:8002/chat/history/your-session-id
```

### Health Check
```bash
curl -X GET http://localhost:8002/health
```

## Project Structure
```
.
├── .github/                    # GitHub specific files
│   └── copilot-instructions.md # Instructions for GitHub Copilot
├── static/                     # Frontend assets for the web interface
│   ├── index.html              # Main web interface HTML
│   ├── script.js               # Frontend JavaScript logic
│   └── styles.css              # CSS styles for the web interface
├── .gitignore                  # Specifies intentionally untracked files for Git
├── IMPLEMENTATION_NOTES.md     # Detailed notes on the chat feature implementation
├── README.md                   # This file: project overview, setup, and API docs
├── comprehensive_test.py       # Comprehensive tests for the application
├── conversation_demo.py        # Interactive script to demo chat features via console
├── index.html                  # Root index.html, likely unused or redirect (static/index.html is primary)
├── requirements.txt            # Python dependencies for the project
├── server.py                   # Main FastAPI application: image classification, sentiment, and chat server
├── simple_server.py            # A lightweight server with mock ML functionalities for quick UI/API testing (runs on port 8001)
├── test_chat.py                # Unit tests for chat functionality
├── test_chat_pipeline.py       # Unit tests for the chat pipeline components
├── test_setup.py               # Tests for setup and environment configuration
└── imagenet_classes.txt        # (Downloaded on first run of server.py) Class labels for ImageNet model
```

## Technical Details

- **Backend Framework**: FastAPI with Uvicorn for ASGI.
- **Machine Learning Models**:
    - Image Classification: ResNet-18 (pretrained on ImageNet) via `torchvision`.
    - Sentiment Analysis: Transformer-based model via Hugging Face `transformers` pipeline.
    - Conversational Chat AI: SmolVLM-Instruct via Hugging Face `transformers` pipeline (`image-text-to-text`).
- **Image Processing**: PIL/Pillow for image handling.
- **Chat**: Supports conversation history, session management, and multimodal (text + image) inputs.
- **Device**: Automatically detects CUDA availability for PyTorch models (CPU fallback).

## Dependencies

Key Python libraries include:
- `fastapi`: Modern web framework for building APIs.
- `uvicorn`: ASGI server for running FastAPI.
- `torch` & `torchvision`: PyTorch deep learning framework and computer vision library.
- `transformers`: Hugging Face library for state-of-the-art NLP models.
- `pillow`: Image processing library.
- `python-multipart`: For parsing form data (e.g., file uploads).

Refer to `requirements.txt` for a full list of dependencies and their versions.

## Development

This project uses a Python virtual environment to manage dependencies. The preferred name is `fastapi_env`.

**Activate the Environment:**

-   **Windows:**
    ```bash
    .\fastapi_env\Scripts\activate
    ```
-   **Linux/macOS:**
    ```bash
    source fastapi_env/bin/activate
    ```

After activating, you can run `python server.py` to start the main application or explore other scripts like `conversation_demo.py`.

## License

This project is for educational and demonstration purposes.
