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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We are using transformers for future extensions, e.g., sentiment analysis
from transformers import (
    pipeline,
)  # Uncomment if you want to use transformers for NLP tasks


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
chat_bot = None

# Try to load a simple text generation model
try:
    # Use a smaller, more reliable model
    chat_bot = pipeline(
        "image-text-to-text",
        model="HuggingFaceTB/SmolVLM-Instruct",
        device=0 if torch.cuda.is_available() else -1,
        torch_dtype=torch.float16,  # More compatible
    )
    print(f"✓ {chat_bot.model.base_model._get_name()} loaded successfully for chat. Running on {device}.")
except Exception as e:
    print(f"✗ Warning: Could not load {chat_bot.model.base_model._get_name()}: {e}")
    chat_bot = None

# For now, let's skip the complex multimodal model to ensure basic functionality works
print("Chat initialization complete")

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
async def chat(message: str = Form(...), image: UploadFile = None):
    """Chat endpoint that provides simple conversational AI.
    Currently supports text-only conversations with image acknowledgment.
    """
    try:
        # Handle image upload (acknowledge but don't process for now)
        if image:
            if image.content_type not in ("image/jpeg", "image/png"):
                raise HTTPException(
                    status_code=415, detail="Please upload a JPEG or PNG image."
                )
            
            # For now, just acknowledge the image
            if chat_bot is not None:
                # Generate response with image context
                prompt = f"User sent an image and said: {message}. Respond helpfully."
                response = chat_bot(
                    image=Image.open(io.BytesIO(await image.read())).convert("RGB"),
                    text=prompt,

                )
                
                if isinstance(response, list) and len(response) > 0:
                    generated_text = response[0].get('generated_text', '')
                    # Remove the prompt from the response
                    if generated_text.startswith(prompt):
                        assistant_response = generated_text[len(prompt):].strip()
                    else:
                        assistant_response = generated_text.strip()
                else:
                    assistant_response = "I can see you sent an image! While I can't analyze it yet, I'm here to help with your message."
            else:
                assistant_response = "I can see you sent an image! While I can't analyze it yet, I'm here to help with your message."
        
        else:
            # Text-only conversation
            if chat_bot is not None:
                # Use the text generation model
                response = chat_bot(
                    text=message,
                )
                
                if isinstance(response, list) and len(response) > 0:
                    generated_text = response[0].get('generated_text', '')
                    # Remove the input from the response
                    if generated_text.startswith(message):
                        assistant_response = generated_text[len(message):].strip()
                    else:
                        assistant_response = generated_text.strip()
                else:
                    assistant_response = "I'm sorry, I couldn't generate a response."
            else:
                # Simple rule-based fallback
                assistant_response = f"I understand you said: '{message}'. I'm a simple AI assistant here to help!"
        
        # Clean up and validate response
        if not assistant_response or len(assistant_response.strip()) == 0:
            assistant_response = "I'm here to help! Could you please rephrase your question?"
        # Log the interaction
        logger.info(f"User: {message} | Assistant: {assistant_response} | Model: {chat_bot.model.base_model._get_name() if chat_bot else 'Simple Rule-based Chat'}")
        return JSONResponse({
            "message": message,
            "response": assistant_response,
            "has_image": image is not None,
            "model_used": chat_bot.model.base_model._get_name() if chat_bot else "Simple Rule-based Chat"
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        # Provide a fallback response even if there's an error
        return JSONResponse({
            "message": message,
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
            "has_image": image is not None,
            "model_used": chat_bot.model.base_model._get_name() if chat_bot else "Error fallback"
        })


# ---------- 4. Entry point ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
