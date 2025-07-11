#!/usr/bin/env python3
"""
Comprehensive test suite for SmolVLM FastAPI server with conversation history.
This test suite validates all functionality including session management and image handling.
"""

import requests
import json
from PIL import Image
import io
import uuid
import time
import os

class ConversationTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, details))
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        print()
    
    def create_test_image(self, color='red', size=(100, 100)):
        """Create a test image."""
        img = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    
    def send_chat_message(self, message, image_path=None, session_id=None):
        """Send a chat message."""
        url = f"{self.base_url}/chat"
        
        data = {"message": message}
        if session_id:
            data["session_id"] = session_id
            
        files = {}
        if image_path:
            if isinstance(image_path, str):
                with open(image_path, 'rb') as f:
                    files["image"] = (image_path, f, "image/png")
                    response = requests.post(url, data=data, files=files)
            else:
                files["image"] = ("test.png", image_path, "image/png")
                response = requests.post(url, data=data, files=files)
        else:
            response = requests.post(url, data=data)
        
        return response.json()
    
    def test_server_health(self):
        """Test if server is running."""
        try:
            response = requests.get(f"{self.base_url}/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}" if not success else ""
            self.log_test("Server Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Server Health Check", False, str(e))
            return False
    
    def test_basic_chat(self):
        """Test basic chat functionality."""
        try:
            response = self.send_chat_message("Hello, how are you?")
            success = 'response' in response and 'session_id' in response
            self.session_id = response.get('session_id')
            details = f"Session ID: {self.session_id}" if success else "Missing required fields"
            self.log_test("Basic Chat", success, details)
            return success
        except Exception as e:
            self.log_test("Basic Chat", False, str(e))
            return False
    
    def test_conversation_memory(self):
        """Test conversation memory."""
        if not self.session_id:
            self.log_test("Conversation Memory", False, "No session ID available")
            return False
        
        try:
            # Send first message with personal info
            response1 = self.send_chat_message("My name is Alice and I'm a programmer", session_id=self.session_id)
            
            # Ask about the information
            response2 = self.send_chat_message("What is my name and profession?", session_id=self.session_id)
            
            # Check if the response mentions Alice or programmer
            response_text = response2.get('response', '').lower()
            success = 'alice' in response_text or 'programmer' in response_text or 'programming' in response_text
            
            details = f"Response: {response2.get('response', '')[:100]}..." if success else "AI didn't remember personal info"
            self.log_test("Conversation Memory", success, details)
            return success
        except Exception as e:
            self.log_test("Conversation Memory", False, str(e))
            return False
    
    def test_image_chat(self):
        """Test image chat functionality."""
        try:
            # Create a blue test image
            test_image = self.create_test_image(color='blue')
            
            response = self.send_chat_message("What color is this image?", image_path=test_image, session_id=self.session_id)
            
            success = 'response' in response and response.get('has_image', False)
            details = f"Has image: {response.get('has_image')}, Response: {response.get('response', '')[:100]}..."
            
            self.log_test("Image Chat", success, details)
            return success
        except Exception as e:
            self.log_test("Image Chat", False, str(e))
            return False
    
    def test_image_memory(self):
        """Test image memory (asking about image without sending it again)."""
        if not self.session_id:
            self.log_test("Image Memory", False, "No session ID available")
            return False
        
        try:
            # Ask about the previously sent image
            response = self.send_chat_message("Can you describe the image I just sent?", session_id=self.session_id)
            
            success = 'response' in response
            details = f"Response: {response.get('response', '')[:100]}..."
            
            self.log_test("Image Memory", success, details)
            return success
        except Exception as e:
            self.log_test("Image Memory", False, str(e))
            return False
    
    def test_history_endpoints(self):
        """Test conversation history management endpoints."""
        if not self.session_id:
            self.log_test("History Endpoints", False, "No session ID available")
            return False
        
        try:
            # Test getting history
            history_response = requests.get(f"{self.base_url}/chat/history/{self.session_id}")
            history_data = history_response.json()
            
            # Test listing sessions
            sessions_response = requests.get(f"{self.base_url}/chat/sessions")
            sessions_data = sessions_response.json()
            
            # Test clearing history
            clear_response = requests.delete(f"{self.base_url}/chat/history/{self.session_id}")
            clear_data = clear_response.json()
            
            success = (history_response.status_code == 200 and 
                      sessions_response.status_code == 200 and 
                      clear_response.status_code == 200 and
                      'history' in history_data and
                      'active_sessions' in sessions_data)
            
            details = f"History length: {history_data.get('length', 0)}, Active sessions: {sessions_data.get('total_sessions', 0)}"
            
            self.log_test("History Endpoints", success, details)
            return success
        except Exception as e:
            self.log_test("History Endpoints", False, str(e))
            return False
    
    def test_multiple_sessions(self):
        """Test multiple concurrent sessions."""
        try:
            # Create two different sessions
            session1 = str(uuid.uuid4())
            session2 = str(uuid.uuid4())
            
            # Send different messages to each session
            response1 = self.send_chat_message("I like cats", session_id=session1)
            response2 = self.send_chat_message("I like dogs", session_id=session2)
            
            # Ask each session about their preference
            response1_check = self.send_chat_message("What do I like?", session_id=session1)
            response2_check = self.send_chat_message("What do I like?", session_id=session2)
            
            # Check if sessions maintain separate contexts
            resp1_text = response1_check.get('response', '').lower()
            resp2_text = response2_check.get('response', '').lower()
            
            success = ('cat' in resp1_text and 'cat' not in resp2_text) or ('dog' in resp2_text and 'dog' not in resp1_text)
            
            details = f"Session 1 remembers: {'cats' if 'cat' in resp1_text else 'unclear'}, Session 2 remembers: {'dogs' if 'dog' in resp2_text else 'unclear'}"
            
            self.log_test("Multiple Sessions", success, details)
            return success
        except Exception as e:
            self.log_test("Multiple Sessions", False, str(e))
            return False
    
    def test_image_replacement(self):
        """Test that only one image is kept in conversation history."""
        try:
            session_id = str(uuid.uuid4())
            
            # Send first image (red)
            red_image = self.create_test_image(color='red')
            self.send_chat_message("What color is this?", image_path=red_image, session_id=session_id)
            
            # Send second image (green)
            green_image = self.create_test_image(color='green')
            self.send_chat_message("What color is this new image?", image_path=green_image, session_id=session_id)
            
            # Ask about the image (should refer to the green one)
            response = self.send_chat_message("What color was the image?", session_id=session_id)
            
            success = 'response' in response
            details = f"Response: {response.get('response', '')[:100]}..."
            
            self.log_test("Image Replacement", success, details)
            return success
        except Exception as e:
            self.log_test("Image Replacement", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and provide summary."""
        print("🧪 SmolVLM Conversation History Test Suite")
        print("=" * 60)
        
        # Run tests in order
        tests = [
            self.test_server_health,
            self.test_basic_chat,
            self.test_conversation_memory,
            self.test_image_chat,
            self.test_image_memory,
            self.test_history_endpoints,
            self.test_multiple_sessions,
            self.test_image_replacement
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("=" * 60)
        print("📊 Test Summary")
        print("-" * 30)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Your SmolVLM server with conversation history is working perfectly!")
        else:
            print(f"\n⚠️  {total-passed} test(s) failed. Please check the server logs and configuration.")
            
        return passed == total

if __name__ == "__main__":
    tester = ConversationTester()
    try:
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        exit(1)
