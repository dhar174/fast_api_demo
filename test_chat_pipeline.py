#!/usr/bin/env python3
"""
Test script to verify the SmolVLM image-text-to-text pipeline implementation with conversation history.
"""

import requests
import json
from PIL import Image
import io
import base64
import uuid

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
        print(f"✓ Session ID: {result['session_id']}")
        return True, result['session_id']
    except Exception as e:
        print(f"✗ Text chat failed: {e}")
        return False, None

def test_conversation_history(session_id):
    """Test conversation history functionality."""
    print("\nTesting conversation history...")
    
    url = "http://localhost:8002/chat"
    
    # First message
    data1 = {
        "message": "My name is Alice. Remember this!",
        "session_id": session_id
    }
    
    # Second message
    data2 = {
        "message": "What is my name?",
        "session_id": session_id
    }
    
    try:
        # Send first message
        response1 = requests.post(url, data=data1)
        result1 = response1.json()
        print(f"✓ First message response: {result1['response']}")
        
        # Send second message
        response2 = requests.post(url, data=data2)
        result2 = response2.json()
        print(f"✓ Second message response: {result2['response']}")
        print(f"✓ Conversation length: {result2['conversation_length']}")
        
        return True
    except Exception as e:
        print(f"✗ Conversation history test failed: {e}")
        return False

def test_image_chat_with_history():
    """Test image + text chat functionality with conversation history."""
    print("\nTesting image + text chat with history...")
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    url = "http://localhost:8002/chat"
    session_id = str(uuid.uuid4())
    
    # First message with image
    data1 = {
        "message": "What color is this image?",
        "session_id": session_id
    }
    files1 = {
        "image": ("test.png", img_bytes, "image/png")
    }
    
    # Second message without image
    data2 = {
        "message": "Can you describe the image again?",
        "session_id": session_id
    }
    
    try:
        # Send first message with image
        response1 = requests.post(url, data=data1, files=files1)
        result1 = response1.json()
        print(f"✓ Image chat response: {result1['response']}")
        print(f"✓ Has image: {result1['has_image']}")
        
        # Send second message without image (should still have context)
        response2 = requests.post(url, data=data2)
        result2 = response2.json()
        print(f"✓ Follow-up response: {result2['response']}")
        print(f"✓ Conversation length: {result2['conversation_length']}")
        
        return True
    except Exception as e:
        print(f"✗ Image chat with history failed: {e}")
        return False

def test_history_endpoints(session_id):
    """Test conversation history management endpoints."""
    print("\nTesting history management endpoints...")
    
    try:
        # Get history
        history_response = requests.get(f"http://localhost:8002/chat/history/{session_id}")
        history_result = history_response.json()
        print(f"✓ History retrieved: {history_result['length']} messages")
        
        # List sessions
        sessions_response = requests.get("http://localhost:8002/chat/sessions")
        sessions_result = sessions_response.json()
        print(f"✓ Active sessions: {sessions_result['total_sessions']}")
        
        # Clear history
        clear_response = requests.delete(f"http://localhost:8002/chat/history/{session_id}")
        clear_result = clear_response.json()
        print(f"✓ History cleared: {clear_result['message']}")
        
        return True
    except Exception as e:
        print(f"✗ History endpoints test failed: {e}")
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
    print("SmolVLM Pipeline with Conversation History Test Suite")
    print("=" * 60)
    
    # Test server health first
    if not test_health_check():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python server.py")
        exit(1)
    
    # Test text-only chat
    text_success, session_id = test_text_only_chat()
    
    # Test conversation history
    history_success = False
    if text_success and session_id:
        history_success = test_conversation_history(session_id)
    
    # Test image + text chat with history
    image_success = test_image_chat_with_history()
    
    # Test history management endpoints
    endpoints_success = False
    if text_success and session_id:
        endpoints_success = test_history_endpoints(session_id)
    
    print("\n" + "=" * 60)
    if text_success and history_success and image_success and endpoints_success:
        print("✅ All tests passed! The SmolVLM pipeline with conversation history is working correctly.")
    else:
        print("❌ Some tests failed. Check the server logs for details.")
        print(f"   Text chat: {'✅' if text_success else '❌'}")
        print(f"   History: {'✅' if history_success else '❌'}")
        print(f"   Image chat: {'✅' if image_success else '❌'}")
        print(f"   Endpoints: {'✅' if endpoints_success else '❌'}")
