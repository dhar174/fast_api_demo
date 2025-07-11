#!/usr/bin/env python3
"""
Test script to verify the SmolVLM image-text-to-text pipeline implementation.
"""

import requests
import json
from PIL import Image
import io
import base64

def test_text_only_chat():
    """Test text-only chat functionality."""
    print("Testing text-only chat...")
    
    url = "http://localhost:8002/chat"
    data = {
        "message": "Hello, how are you today?"
    }
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        print(f"✓ Text chat response: {result['response']}")
        print(f"✓ Model used: {result['model_used']}")
        return True
    except Exception as e:
        print(f"✗ Text chat failed: {e}")
        return False

def test_image_chat():
    """Test image + text chat functionality."""
    print("\nTesting image + text chat...")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    url = "http://localhost:8002/chat"
    data = {
        "message": "What do you see in this image?"
    }
    files = {
        "image": ("test.png", img_bytes, "image/png")
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        result = response.json()
        print(f"✓ Image chat response: {result['response']}")
        print(f"✓ Model used: {result['model_used']}")
        print(f"✓ Has image: {result['has_image']}")
        return True
    except Exception as e:
        print(f"✗ Image chat failed: {e}")
        return False

def test_health_check():
    """Test if the server is running."""
    print("Testing server health...")
    
    try:
        response = requests.get("http://localhost:8002/health")
        result = response.json()
        print(f"✓ Server health: {result['msg']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("SmolVLM Pipeline Test Suite")
    print("=" * 40)
    
    # Test server health first
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python server.py")
        exit(1)
    
    # Test text-only chat
    text_success = test_text_only_chat()
    
    # Test image + text chat
    image_success = test_image_chat()
    
    print("\n" + "=" * 40)
    if text_success and image_success:
        print("✅ All tests passed! The SmolVLM pipeline is working correctly.")
    else:
        print("❌ Some tests failed. Check the server logs for details.")
