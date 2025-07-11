"""
Simple chat endpoint test to verify the basic functionality works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import torch
from PIL import Image
import io

app = FastAPI()

# Simple echo-based chat for testing
@app.post("/chat")
async def chat(message: str, image: UploadFile = None):
    """Simple chat endpoint for testing"""
    try:
        response_text = f"Echo: {message}"
        
        if image:
            # Just acknowledge the image
            response_text += " (I can see you sent an image, but I'm in simple mode)"
            
        return JSONResponse({
            "message": message,
            "response": response_text,
            "has_image": image is not None,
            "model_used": "Simple Echo"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

if __name__ == "__main__":
    print("Simple chat test working!")
