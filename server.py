"""
Minimal FastAPI image-classifier demo.
• Loads a pretrained ResNet-18 from torchvision (no model file to download ahead of time).
• Accepts an image upload and returns the top-1 class label.
Run:
    pip install fastapi uvicorn torch torchvision pillow
    python server.py
Open:
    http://localhost:8000/docs   ← interactive Swagger UI
"""

from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import torch
from torchvision import models, transforms
from PIL import Image
import io
import json
import urllib.request
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We are using transformers for future extensions, e.g., sentiment analysis
from transformers import (
    pipeline,
)  # Using pipeline for image-text-to-text tasks


app = FastAPI(title="Minimal FastAPI Image Classifier")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- 1. Load model & labels ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


print(f"Using device: {device}")
# Load a pretrained ResNet-18 model
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.eval().to(device)

sentiment_analyzer = pipeline(
    "sentiment-analysis", device=0 if torch.cuda.is_available() else -1
)

# Initialize chat capabilities
print("Initializing chat models...")

# Initialize chat model using transformers pipeline
chat_bot = None

try:
    # Use image-text-to-text pipeline for SmolVLM
    chat_bot = pipeline(
        "image-text-to-text",
        model="HuggingFaceTB/SmolVLM-Instruct",
        device=0 if torch.cuda.is_available() else -1,
        torch_dtype=torch.float16,
    )
    print(f"✓ SmolVLM-Instruct loaded successfully for chat using pipeline. Running on {device}.")
except Exception as e:
    print(f"✗ Warning: Could not load SmolVLM-Instruct: {e}")
    chat_bot = None

# Ensure the chat model is ready
if chat_bot is not None:
    try:
        # Test the chat model with a simple prompt
        test_messages = [
            {"role": "user", "content": [{"type": "text", "text": "Hello, how are you?"}]}
        ]
        test_response = chat_bot(text=test_messages, max_new_tokens=50, return_full_text=False)
        print(f"Chat model initialized successfully: {test_response}")
    except Exception as e:
        print(f"Error during chat model initialization: {e}")

print("Chat initialization complete")

# ---------- Conversation History Management ----------
# In-memory storage for conversation histories
# In production, you'd want to use a database like Redis or PostgreSQL
conversation_histories: Dict[str, List[Dict[str, Any]]] = {}

def get_or_create_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Get existing conversation history or create a new one."""
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    return conversation_histories[session_id]

def add_to_conversation_history(session_id: str, role: str, content: List[Dict[str, Any]]) -> None:
    """Add a message to the conversation history."""
    history = get_or_create_conversation_history(session_id)
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # Limit history to last 10 exchanges (20 messages) to prevent memory issues
    if len(history) > 20:
        history[:] = history[-20:]

def clean_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Clean conversation history to ensure only one image is kept."""
    history = get_or_create_conversation_history(session_id)
    
    # Find the most recent message with an image
    last_image_index = -1
    for i in range(len(history) - 1, -1, -1):
        if history[i]["role"] == "user":
            for content_item in history[i]["content"]:
                if content_item.get("type") == "image":
                    last_image_index = i
                    break
        if last_image_index != -1:
            break
    
    # Remove images from all messages except the most recent one
    cleaned_history = []
    for i, message in enumerate(history):
        cleaned_message = {
            "role": message["role"],
            "content": []
        }
        
        for content_item in message["content"]:
            if content_item.get("type") == "image":
                # Only keep the image if this is the most recent message with an image
                if i == last_image_index:
                    cleaned_message["content"].append(content_item)
            else:
                cleaned_message["content"].append(content_item)
        
        # Only add the message if it has content
        if cleaned_message["content"]:
            cleaned_history.append(cleaned_message)
    
    return cleaned_history

# Download ImageNet labels (only once)
LABELS_PATH = "imagenet_classes.txt"
if not os.path.exists(LABELS_PATH):
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt",
        "imagenet_classes.txt",
    )

# Read labels into a list
with open("imagenet_classes.txt") as f:
    LABELS = [line.strip() for line in f.readlines()]

# ---------- 2. Pre-processing pipeline ----------
preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet means
            std=[0.229, 0.224, 0.225],  # ImageNet stds
        ),
    ]
)


# ---------- 3. Routes ----------
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r") as ff:
        return HTMLResponse(content=ff.read(), status_code=200)


@app.get("/health")
def health():
    return {"msg": "Up and running!  Visit /docs for Swagger UI."}


@app.post("/predict")
async def predict(file: UploadFile):
    # 3-A. Safety checks
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=415, detail="Please upload a JPEG or PNG image."
        )

    # 3-B. Read image bytes -> PIL Image
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # 3-C. Pre-process → tensor
    tensor = preprocess(image).unsqueeze(0).to(device)

    # 3-D. Inference
    with torch.no_grad():
        outputs = model(tensor)
    prob = torch.nn.functional.softmax(outputs[0], dim=0)
    top_idx = torch.argmax(prob).item()
    top_label = LABELS[top_idx]
    confidence = prob[top_idx].item()
    logger.info(f"Predicted: {top_label} with confidence {confidence:.4f}") 
    # 3-E. Return JSON
    return JSONResponse(
        {
            "filename": file.filename,
            "predicted_class": top_label,
            "confidence": round(confidence, 4),
        }
    )


@app.get("/sentiment_analysis")
async def sentiment_analysis(text: str):
    """
    Example endpoint for sentiment analysis using transformers.
    This is just a placeholder to show how you might extend the app.
    """
    result = sentiment_analyzer(text)
    return JSONResponse({"text": text, "sentiment": result[0]})


@app.post("/chat")
async def chat(message: str = Form(...), image: UploadFile = None, session_id: str = Form(None)):
    """Chat endpoint that provides conversational AI with image understanding.
    Uses SmolVLM pipeline for multimodal conversations with conversation history.
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        # Prepare the current user message content
        current_content = []
        pil_image = None
        
        # Handle image upload
        if image:
            if image.content_type not in ("image/jpeg", "image/png"):
                raise HTTPException(
                    status_code=415, detail="Please upload a JPEG or PNG image."
                )
            
            # Convert image to PIL
            img_bytes = await image.read()
            pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            current_content.append({"type": "image"})
        
        # Add text message
        current_content.append({"type": "text", "text": message})
        
        # Add current user message to history
        add_to_conversation_history(session_id, "user", current_content)
        
        # Get cleaned conversation history (with only one image)
        conversation_history = clean_conversation_history(session_id)
        
        # Process with chat model
        if chat_bot is not None:
            # Prepare messages for the pipeline
            messages = conversation_history.copy()
            
            # Collect images from the conversation history
            images = []
            for msg in messages:
                if msg["role"] == "user":
                    for content_item in msg["content"]:
                        if content_item.get("type") == "image":
                            if pil_image is not None:
                                images.append(pil_image)
                            break
            
            # Generate response using pipeline with proper parameters
            if images:
                response = chat_bot(
                    text=messages, 
                    images=images, 
                    max_new_tokens=256, 
                    return_full_text=False
                )
            else:
                response = chat_bot(
                    text=messages, 
                    max_new_tokens=256, 
                    return_full_text=False
                )
            
            # Extract assistant response
            if isinstance(response, list) and len(response) > 0:
                assistant_response = response[0].get('generated_text', '').strip()
            elif isinstance(response, str):
                assistant_response = response.strip()
            else:
                assistant_response = "I'm here to help! Could you please rephrase your question?"
            
            if not assistant_response:
                if images:
                    assistant_response = "I can see your image! How can I help you with it?"
                else:
                    assistant_response = "I'm here to help! Could you please rephrase your question?"
        else:
            # Simple rule-based fallback
            if image:
                assistant_response = "I can see you sent an image! While I can't analyze it yet, I'm here to help with your message."
            else:
                assistant_response = f"I understand you said: '{message}'. I'm a simple AI assistant here to help!"
        
        # Clean up and validate response
        if not assistant_response or len(assistant_response.strip()) == 0:
            assistant_response = "I'm here to help! Could you please rephrase your question?"
        
        # Add assistant response to history
        add_to_conversation_history(session_id, "assistant", [{"type": "text", "text": assistant_response}])
        
        # Log the interaction
        model_name = "SmolVLM-Instruct" if chat_bot is not None else "Simple Rule-based Chat"
        logger.info(f"Session {session_id[:8]}... | User: {message} | Assistant: {assistant_response} | Model: {model_name}")
        
        return JSONResponse({
            "message": message,
            "response": assistant_response,
            "has_image": image is not None,
            "model_used": model_name,
            "session_id": session_id,
            "conversation_length": len(conversation_histories.get(session_id, []))
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)} | Message: {message} | Image: {image.filename if image else 'None'} | Session: {session_id}")
        # Provide a fallback response even if there's an error
        return JSONResponse({
            "message": message,
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
            "has_image": image is not None,
            "model_used": "Error fallback",
            "session_id": session_id,
            "conversation_length": len(conversation_histories.get(session_id, []))
        })


@app.get("/chat/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get the conversation history for a specific session."""
    history = conversation_histories.get(session_id, [])
    return JSONResponse({
        "session_id": session_id,
        "history": history,
        "length": len(history)
    })

@app.delete("/chat/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear the conversation history for a specific session."""
    if session_id in conversation_histories:
        del conversation_histories[session_id]
        return JSONResponse({"message": f"Conversation history cleared for session {session_id}"})
    else:
        return JSONResponse({"message": f"No conversation history found for session {session_id}"})

@app.get("/chat/sessions")
async def list_active_sessions():
    """List all active conversation sessions."""
    sessions = []
    for session_id, history in conversation_histories.items():
        sessions.append({
            "session_id": session_id,
            "message_count": len(history),
            "last_updated": history[-1]["timestamp"] if history else None
        })
    return JSONResponse({"active_sessions": sessions, "total_sessions": len(sessions)})


# ---------- 4. Entry point ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
