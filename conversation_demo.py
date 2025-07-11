#!/usr/bin/env python3
"""
Example script demonstrating conversation history with SmolVLM FastAPI server.
"""

import requests
import json
from PIL import Image
import io
import uuid

class ChatClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        
    def send_message(self, message, image_path=None):
        """Send a message to the chat endpoint."""
        url = f"{self.base_url}/chat"
        
        data = {
            "message": message,
            "session_id": self.session_id
        }
        
        files = {}
        if image_path:
            with open(image_path, 'rb') as f:
                files["image"] = (image_path, f, "image/jpeg")
                response = requests.post(url, data=data, files=files)
        else:
            response = requests.post(url, data=data)
        
        return response.json()
    
    def get_history(self):
        """Get conversation history."""
        url = f"{self.base_url}/chat/history/{self.session_id}"
        response = requests.get(url)
        return response.json()
    
    def clear_history(self):
        """Clear conversation history."""
        url = f"{self.base_url}/chat/history/{self.session_id}"
        response = requests.delete(url)
        return response.json()

def demo_conversation():
    """Demonstrate a conversation with memory."""
    print("🤖 SmolVLM Conversation Demo")
    print("=" * 50)
    
    client = ChatClient()
    
    # Step 1: Introduction
    print("\n1. Introducing myself...")
    response = client.send_message("Hello! My name is Alice and I'm a software developer.")
    print(f"   Assistant: {response['response']}")
    
    # Step 2: Ask about memory
    print("\n2. Testing memory...")
    response = client.send_message("What is my name and profession?")
    print(f"   Assistant: {response['response']}")
    
    # Step 3: Create a test image and ask about it
    print("\n3. Sending an image...")
    # Create a simple test image
    img = Image.new('RGB', (200, 200), color='blue')
    img.save('/tmp/test_image.png')
    
    response = client.send_message("What color is this image?", "/tmp/test_image.png")
    print(f"   Assistant: {response['response']}")
    
    # Step 4: Ask about the image without sending it again
    print("\n4. Asking about the image again (without sending it)...")
    response = client.send_message("Can you describe the image I just sent?")
    print(f"   Assistant: {response['response']}")
    
    # Step 5: Show conversation history
    print("\n5. Conversation history:")
    history = client.get_history()
    print(f"   Total messages: {history['length']}")
    for i, msg in enumerate(history['history']):
        role = msg['role']
        content_text = ""
        has_image = False
        
        for content in msg['content']:
            if content['type'] == 'text':
                content_text = content['text']
            elif content['type'] == 'image':
                has_image = True
        
        image_indicator = " 🖼️" if has_image else ""
        print(f"   {i+1}. {role.capitalize()}: {content_text}{image_indicator}")
    
    # Step 6: Clear history
    print("\n6. Clearing conversation history...")
    clear_result = client.clear_history()
    print(f"   {clear_result['message']}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    try:
        demo_conversation()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Please make sure the server is running: python server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
