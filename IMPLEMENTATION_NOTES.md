# SmolVLM Image-Text-to-Text Pipeline with Conversation History

## Overview
This implementation uses the Hugging Face Transformers `image-text-to-text` pipeline to integrate SmolVLM-Instruct for multimodal conversations in your FastAPI application. Now includes conversation history management with intelligent image handling.

## Key Features Added

### 1. Conversation History Management
- **Session-based conversations**: Each chat session maintains its own conversation history
- **Memory persistence**: Conversations are remembered across multiple requests
- **Automatic session management**: Session IDs are auto-generated if not provided
- **History cleanup**: Automatic removal of old messages to prevent memory issues

### 2. Intelligent Image Handling
- **Single image constraint**: Only one image is kept in conversation history at a time
- **Image context preservation**: The most recent image is maintained for context
- **Memory optimization**: Older images are automatically removed from history

### 3. Enhanced API Endpoints
- **POST `/chat`**: Main chat endpoint with session support
- **GET `/chat/history/{session_id}`**: Retrieve conversation history
- **DELETE `/chat/history/{session_id}`**: Clear conversation history
- **GET `/chat/sessions`**: List all active sessions

## API Documentation

### POST `/chat`
Enhanced chat endpoint with conversation history support.

**Parameters:**
- `message` (required): The text message
- `image` (optional): Image file (JPEG/PNG)
- `session_id` (optional): Session ID for conversation continuity

**Response:**
```json
{
  "message": "User's message",
  "response": "Assistant's response",
  "has_image": true,
  "model_used": "SmolVLM-Instruct",
  "session_id": "uuid-string",
  "conversation_length": 4
}
```

### GET `/chat/history/{session_id}`
Retrieve conversation history for a specific session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "history": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Hello!"}
      ],
      "timestamp": "2025-01-01T12:00:00.000Z"
    },
    {
      "role": "assistant",
      "content": [
        {"type": "text", "text": "Hi there!"}
      ],
      "timestamp": "2025-01-01T12:00:01.000Z"
    }
  ],
  "length": 2
}
```

### DELETE `/chat/history/{session_id}`
Clear conversation history for a specific session.

### GET `/chat/sessions`
List all active conversation sessions.

## Usage Examples

### Basic Conversation
```bash
# Start a new conversation
curl -X POST "http://localhost:8002/chat" \
  -F "message=Hello, my name is Alice"

# Continue the conversation (use the session_id from previous response)
curl -X POST "http://localhost:8002/chat" \
  -F "message=What is my name?" \
  -F "session_id=your-session-id"
```

### Image + Text Conversation
```bash
# Send an image with a question
curl -X POST "http://localhost:8002/chat" \
  -F "message=What do you see in this image?" \
  -F "image=@photo.jpg" \
  -F "session_id=your-session-id"

# Ask about the image again without sending it
curl -X POST "http://localhost:8002/chat" \
  -F "message=Can you describe the image again?" \
  -F "session_id=your-session-id"
```

### Conversation Management
```bash
# Get conversation history
curl "http://localhost:8002/chat/history/your-session-id"

# Clear conversation history
curl -X DELETE "http://localhost:8002/chat/history/your-session-id"

# List active sessions
curl "http://localhost:8002/chat/sessions"
```

## Message Format Structure
Messages are now formatted according to the chat template standard:
```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},  # For images
            {"type": "text", "text": "Your message here"}
        ],
        "timestamp": "2025-01-01T12:00:00.000Z"
    },
    {
        "role": "assistant", 
        "content": [
            {"type": "text", "text": "Assistant response"}
        ],
        "timestamp": "2025-01-01T12:00:01.000Z"
    }
]
```

## Image Handling Logic
1. **New image uploaded**: Replaces any existing image in conversation history
2. **No image uploaded**: Maintains the most recent image for context
3. **Multiple images**: Only the most recent image is kept in history
4. **Image context**: The image remains available for follow-up questions

## Memory Management
- **History limit**: Maximum 20 messages (10 exchanges) per session
- **Auto-cleanup**: Oldest messages are automatically removed
- **Image optimization**: Only one image stored per conversation
- **Session cleanup**: Sessions can be manually cleared via API

## Testing
Run the comprehensive test suite:
```bash
# Basic functionality test
python test_chat_pipeline.py

# Interactive conversation demo
python conversation_demo.py
```

## Benefits of Conversation History
1. **Context Awareness**: Model remembers previous interactions
2. **Natural Flow**: Conversations feel more natural and coherent
3. **Image Memory**: Can refer back to images without re-uploading
4. **Session Management**: Multiple concurrent conversations supported
5. **Memory Efficiency**: Intelligent cleanup prevents memory bloat

## Production Considerations
- **Database Storage**: Replace in-memory storage with Redis/PostgreSQL for production
- **Session Persistence**: Consider persistent storage for longer conversations
- **Rate Limiting**: Implement rate limiting per session
- **Image Storage**: Consider cloud storage for images in production
- **Monitoring**: Add metrics for conversation lengths and session counts
