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

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import torch
from torchvision import models, transforms
from PIL import Image
import io
import json
import urllib.request
import os

# We are using transformers for future extensions, e.g., sentiment analysis
from transformers import (
    pipeline,
)  # Uncomment if you want to use transformers for NLP tasks


app = FastAPI(title="Minimal FastAPI Image Classifier")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- 1. Load model & labels ----------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

assert device is not "cpu", "No CUDA device found, using CPU instead."

print(f"Using device: {device}")
# Load a pretrained ResNet-18 model
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.eval().to(device)

sentiment_analyzer = pipeline(
    "sentiment-analysis", device=0 if torch.cuda.is_available() else -1
)


chat_bot = pipeline(
    "text-generation",
    model="HuggingFaceTB/SmolVLM-Instruct",
    device=0 if torch.cuda.is_available() else -1,
    torch_dtype=torch.float16,
)

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
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


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


async def messages_builder(message: str, image: UploadFile = None):
    messages = [{"role": "user", "content": [{"type": "text", "text": message}]}]
    if image:
        if image.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(
                status_code=415, detail="Please upload a JPEG or PNG image."
            )

        # 3-B. Read image bytes -> PIL Image
        img_bytes = await image.read()
        rgb_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        messages[0]["content"].append({"type": "image", "data": rgb_image})
    return messages


@app.post("/chat")
async def chat(message: str, image: UploadFile = None):
    """Example chat endpoint that uses the chat_bot pipeline.
    If an image is provided, it can be processed as well.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG",
                },
                {"type": "text", "text": "What animal is on the candy?"},
            ],
        },
    ]
    response = chat_bot(messages)

    print(f"Chat response: {response[0]}")
    # Assuming response is a list with a dictionary containing 'generated_text'
    return JSONResponse({"message": message, "response": response[0]})


# ---------- 4. Entry point ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
