# FastAPI Image Classifier with Web Interface

A modern FastAPI application that performs image classification using ResNet-18 and sentiment analysis using transformers, complete with a beautiful web interface.

## Features

- **🖼️ Image Classification**: Upload images for real-time classification using ResNet-18
- **💭 Sentiment Analysis**: Analyze text sentiment using transformer models  
- **🌐 Web Interface**: Modern, responsive frontend with drag-and-drop functionality
- **📊 Interactive Results**: Visual confidence scores and sentiment indicators
- **⚡ Real-time Processing**: Fast inference with PyTorch and transformers
- **📱 Mobile Friendly**: Responsive design that works on all devices

## Quick Start

### 1. Install Dependencies

```bash
# The virtual environment is already created as .venv
# Activate it with:
.venv/Scripts/activate  # On Windows
# or source .venv/bin/activate  # On Linux/Mac

# Install packages (if needed)
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Using the virtual environment Python executable
.venv/Scripts/python.exe server.py

# Or activate the environment first
.venv/Scripts/activate
python server.py
```

The server will start on `http://localhost:8000`

### 3. Access the Application

**🌐 Web Interface (Recommended)**: Open [http://localhost:8000](http://localhost:8000)
- Modern, user-friendly interface
- Drag-and-drop image upload
- Real-time sentiment analysis
- Visual progress indicators

**📚 API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive Swagger UI
- Test API endpoints directly
- View request/response schemas

## API Endpoints

### GET `/`
Serves the main web interface with modern UI for image classification and sentiment analysis.

### GET `/health`
Health check endpoint that returns server status.

### POST `/predict`
Image classification endpoint that accepts an image file and returns the predicted class.

**Request**: Multipart form data with an image file
**Response**: JSON with filename, predicted class, and confidence score

```json
{
  "filename": "dog.jpg",
  "predicted_class": "golden_retriever",
  "confidence": 0.8234
}
```

### GET `/sentiment_analysis`
Sentiment analysis endpoint that analyzes the sentiment of provided text.

**Parameters**: `text` (query parameter)
**Response**: JSON with text and sentiment analysis

```json
{
  "text": "I love this application!",
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.9998
  }
}
```

## Project Structure

```
fast_api_demo/
├── server.py                 # Main FastAPI application
├── requirements.txt          # Python dependencies
├── static/                   # Frontend assets
│   ├── index.html           # Main web interface
│   ├── styles.css           # Styling
│   └── script.js            # Frontend functionality
├── .venv/                   # Virtual environment
├── .github/
│   └── copilot-instructions.md
└── README.md
```

## Technical Details

- **Model**: ResNet-18 pretrained on ImageNet
- **Framework**: FastAPI with Uvicorn server
- **Image Processing**: PIL/Pillow for image handling
- **Preprocessing**: Standard ImageNet preprocessing pipeline
- **Device**: Automatically detects CUDA availability

## Dependencies

- `fastapi` - Modern web framework for building APIs
- `uvicorn` - ASGI server for running FastAPI
- `torch` - PyTorch deep learning framework
- `torchvision` - Computer vision library with pretrained models
- `pillow` - Image processing library
- `python-multipart` - Form data parsing for file uploads
- `transformers` - State-of-the-art NLP models

## Development

The project uses a virtual environment to manage dependencies. Make sure to activate it before running any commands:

```bash
source fastapi_env/bin/activate  # On Windows: fastapi_env\Scripts\activate
```

## License

This project is for educational purposes.
