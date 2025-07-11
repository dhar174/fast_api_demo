# SmolVLM Image-Text-to-Text Pipeline Implementation

## Overview
This implementation uses the Hugging Face Transformers `image-text-to-text` pipeline to integrate SmolVLM-Instruct for multimodal conversations in your FastAPI application.

## Key Changes Made

### 1. Pipeline-Based Approach
- **Before**: Used manual model and processor loading with `AutoProcessor` and `AutoModelForVision2Seq`
- **After**: Using `pipeline("image-text-to-text", model="HuggingFaceTB/SmolVLM-Instruct")` for simpler integration

### 2. Proper Message Formatting
Messages are now formatted according to the chat template standard:
```python
messages = [
    {
        "role": "user", 
        "content": [
            {"type": "image"},  # For images
            {"type": "text", "text": "Your message here"}
        ]
    }
]
```

### 3. Pipeline Usage
- **With Image**: `chat_bot(text=messages, images=[pil_image], max_new_tokens=256, return_full_text=False)`
- **Text Only**: `chat_bot(text=messages, max_new_tokens=256, return_full_text=False)`

### 4. Response Handling
- Using `return_full_text=False` to avoid getting the input prompt back in the response
- Proper error handling and fallback responses
- Clean response extraction from pipeline output

## API Endpoints

### POST `/chat`
- **Parameters**: 
  - `message`: The text message (required)
  - `image`: Optional image file (JPEG/PNG)
- **Returns**: JSON with response, model info, and image status

### Examples:
```bash
# Text-only chat
curl -X POST "http://localhost:8002/chat" -F "message=Hello, how are you?"

# Image + text chat
curl -X POST "http://localhost:8002/chat" -F "message=What do you see?" -F "image=@photo.jpg"
```

## Testing
Run the test script to verify functionality:
```bash
python test_chat_pipeline.py
```

## Features
- ✅ Text-only conversations
- ✅ Image understanding and analysis
- ✅ Proper error handling
- ✅ Fallback responses
- ✅ Logging and monitoring
- ✅ Pipeline-based implementation
- ✅ Chat template formatting

## Model Details
- **Model**: HuggingFaceTB/SmolVLM-Instruct
- **Type**: Vision-Language Model (VLM)
- **Capabilities**: Image understanding, text generation, multimodal conversations
- **Memory**: Optimized for efficient inference (~5GB VRAM)

## Benefits of Pipeline Approach
1. **Simplicity**: Less boilerplate code
2. **Robustness**: Built-in error handling
3. **Compatibility**: Better integration with Transformers library
4. **Performance**: Optimized inference pipeline
5. **Maintenance**: Easier to update and maintain
