# FastAPI Image Classifier

A minimal FastAPI application that performs image classification using a pretrained ResNet-18 model from torchvision.

## Features

- **Simple API**: Single endpoint for image classification
- **Pretrained Model**: Uses ResNet-18 trained on ImageNet
- **Interactive Documentation**: Built-in Swagger UI
- **File Upload**: Accepts JPEG and PNG images
- **JSON Response**: Returns predicted class and confidence score

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

### 3. Test the API

Open your browser and go to [http://localhost:8000/docs](http://localhost:8000/docs) to access the interactive Swagger UI.

- Click on the `/predict` endpoint
- Click "Try it out"
- Upload a JPEG or PNG image
- Click "Execute" to get the classification result

## API Endpoints

### GET `/`
Health check endpoint that returns a welcome message.

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

## Project Structure

```
fast_api_demo/
├── server.py              # Main FastAPI application
├── requirements.txt       # Python dependencies
├── fastapi_env/          # Virtual environment (not tracked)
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

## Development

The project uses a virtual environment to manage dependencies. Make sure to activate it before running any commands:

```bash
source fastapi_env/bin/activate  # On Windows: fastapi_env\Scripts\activate
```

## License

This project is for educational purposes.
