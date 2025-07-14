"""
Simplified FastAPI server for testing the chat functionality
"""
from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import io
import json
import urllib.request
import os

app = FastAPI(title="AI MultiModal Hub")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple in-memory chat responses
CHAT_RESPONSES = [
    "That's interesting! Tell me more.",
    "I understand. How can I help you with that?",
    "That's a great question! Let me think about that.",
    "I see what you mean. Can you elaborate?",
    "Thanks for sharing that with me!",
    "That's really cool! What else would you like to know?",
    "I'm here to help! What can I assist you with?",
    "That's a good point. Have you considered other options?",
    "I appreciate you asking! Let me help you with that.",
    "That sounds like something worth exploring further!"
]

import random

@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Server is running!</h1><p>Frontend files not found.</p>", status_code=200)

@app.get("/health")
def health():
    return {"msg": "Up and running! Chat is available.", "status": "healthy"}

@app.post("/chat")
async def chat(message: str = Form(...), image: UploadFile = None):
    """Simple chat endpoint that provides conversational responses"""
    try:
        # Handle image upload
        if image:
            if image.content_type not in ("image/jpeg", "image/png"):
                raise HTTPException(
                    status_code=415, detail="Please upload a JPEG or PNG image."
                )
            
            # Just acknowledge the image for now
            response = f"I can see you uploaded an image! About your message '{message}' - {random.choice(CHAT_RESPONSES)}"
        else:
            # Generate a simple response
            if len(message.strip()) == 0:
                response = "I'm here to help! What would you like to talk about?"
            elif "hello" in message.lower() or "hi" in message.lower():
                response = "Hello! It's nice to meet you. How are you doing today?"
            elif "how are you" in message.lower():
                response = "I'm doing great, thank you for asking! I'm here and ready to help."
            elif "thank" in message.lower():
                response = "You're very welcome! I'm glad I could help."
            elif "?" in message:
                response = f"That's a great question about '{message}'. {random.choice(CHAT_RESPONSES)}"
            else:
                response = f"I hear you saying '{message}'. {random.choice(CHAT_RESPONSES)}"
        
        return JSONResponse({
            "message": message,
            "response": response,
            "has_image": image is not None,
            "model_used": "Simple Rule-based Chat"
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return JSONResponse({
            "message": message or "",
            "response": "I'm sorry, I'm having trouble right now. Please try again!",
            "has_image": image is not None,
            "model_used": "Error fallback"
        })

@app.get("/sentiment_analysis")
async def sentiment_analysis(text: str):
    """Simple sentiment analysis"""
    # Basic sentiment analysis
    positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "happy", "joy"]
    negative_words = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "sad", "angry", "disappointed"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = {"label": "POSITIVE", "score": 0.8}
    elif negative_count > positive_count:
        sentiment = {"label": "NEGATIVE", "score": 0.8}
    else:
        sentiment = {"label": "NEUTRAL", "score": 0.5}
    
    return JSONResponse({"text": text, "sentiment": sentiment})

if __name__ == "__main__":
    import uvicorn
    print("Starting simplified FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
