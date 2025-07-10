<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# FastAPI Image Classifier Project Instructions

This is a FastAPI image classifier project that uses PyTorch and torchvision for image classification.

## Project Structure
- `server.py` - Main FastAPI application with image classification endpoint
- `requirements.txt` - Python dependencies
- `fastapi_env/` - Virtual environment (not tracked in git)

## Key Technologies
- FastAPI for the web framework
- PyTorch/torchvision for machine learning model (ResNet-18)
- PIL/Pillow for image processing
- Uvicorn as the ASGI server

## Development Guidelines
- Use the virtual environment `fastapi_env` for all Python operations
- Follow FastAPI best practices for API development
- Handle image uploads with proper validation
- Return structured JSON responses
- Use proper error handling with HTTPException

## Running the Application
1. Activate the virtual environment: `source fastapi_env/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python server.py`
4. Access the API docs at: http://localhost:8000/docs
