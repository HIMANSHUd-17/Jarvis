# JARVIS API Reference

Complete WebSocket API documentation for JARVIS backend.

## Base URL

```
ws://localhost:8765
```

## Message Format

All messages are JSON objects with consistent structure:

### Request Format
```json
{
  "command": "command_name",
  "param1": "value1",
  "param2": "value2"
}
```

### Response Format
```json
{
  "type": "response|state_update|error",
  "data": {
    "...": "..."
  }
}
```

## Commands

### 1. Get Current State

**Request:**
```json
{
  "command": "get_state"
}
```

**Response:**
```json
{
  "type": "state_update",
  "data": {
    "state": "Idle",
    "context": {},
    "last_user_input": null,
    "last_response": null,
    "timestamp": "2024-05-29T10:30:15.123456"
  }
}
```

### 2. Start Listening

Start audio capture and wake-word detection.

**Request:**
```json
{
  "command": "start_listening"
}
```

**Response:**
```json
{
  "type": "state_update",
  "data": {
    "state": "Listening",
    "...": "..."
  }
}
```

### 3. Stop Listening

Stop audio capture and wake-word detection.

**Request:**
```json
{
  "command": "stop_listening"
}
```

**Response:**
```json
{
  "type": "state_update",
  "data": {
    "state": "Idle",
    "...": "..."
  }
}
```

### 4. Send Text Input

Send text directly to LLM for processing.

**Request:**
```json
{
  "command": "send_text",
  "input": "What's the weather today?"
}
```

**Response:**
```json
{
  "type": "response",
  "data": {
    "input": "What's the weather today?",
    "response": "I don't have real-time weather data, but I can open your browser to check weather.com",
    "action": null,
    "action_params": null
  }
}
```

### 5. Execute System Command

Execute OS-level commands safely.

**Request:**
```json
{
  "command": "execute_command",
  "command_name": "chrome",
  "args": ["https://example.com"]
}
```

**Response:**
```json
{
  "type": "response",
  "data": {
    "type": "command_result",
    "command": "chrome",
    "result": {
      "success": true,
      "message": "Chrome opened with https://example.com"
    }
  }
}
```

**Allowed Commands:**
- `chrome` - Launch Chrome browser (optional URL arg)
- `notepad` - Launch Notepad
- `calculator` - Launch Calculator
- `explorer` - Launch File Explorer (optional path arg)
- `vlc` - Launch VLC media player

### 6. Send WhatsApp Message

Send WhatsApp message to a contact.

**Request:**
```json
{
  "command": "send_whatsapp",
  "contact": "Mom",
  "message": "Hi, I'm on my way home"
}
```

**Response:**
```json
{
  "type": "response",
  "data": {
    "type": "whatsapp_result",
    "result": {
      "success": true,
      "message": "Message sent to Mom",
      "contact": "Mom",
      "text": "Hi, I'm on my way home"
    }
  }
}
```

### 7. Send WhatsApp Group Message

Send message to a WhatsApp group.

**Request:**
```json
{
  "command": "send_group_message",
  "group": "Family",
  "message": "Family dinner at 7 PM"
}
```

**Response:**
```json
{
  "type": "response",
  "data": {
    "type": "whatsapp_result",
    "result": {
      "success": true,
      "message": "Message sent to group Family",
      "group": "Family",
      "text": "Family dinner at 7 PM"
    }
  }
}
```

## State Values

The following state values are returned by the server:

```
- "Idle"       - Waiting for input
- "Listening"  - Capturing audio
- "Processing" - Analyzing input
- "Speaking"   - Playing audio response
- "Error"      - Error occurred
```

## Error Handling

### Error Response
```json
{
  "type": "error",
  "data": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

### Common Errors
- `INVALID_COMMAND` - Unknown command
- `NOT_CONNECTED` - Server disconnected
- `INVALID_JSON` - Malformed JSON
- `COMMAND_FAILED` - Command execution failed
- `CONTACT_NOT_FOUND` - WhatsApp contact not found

## WebSocket Client Example

```javascript
class JarvisClient {
    constructor(host = 'localhost', port = 8765) {
        this.ws = new WebSocket(`ws://${host}:${port}`);
        this.ws.onmessage = (event) => this.handleMessage(event);
    }
    
    send(data) {
        this.ws.send(JSON.stringify(data));
    }
    
    startListening() {
        this.send({ command: 'start_listening' });
    }
    
    sendText(input) {
        this.send({ command: 'send_text', input });
    }
    
    handleMessage(event) {
        const data = JSON.parse(event.data);
        console.log('Message:', data);
    }
}

// Usage
const client = new JarvisClient();
client.startListening();
```

## Rate Limiting

- No strict rate limiting implemented
- Recommended: 1 command per 100ms to prevent server overload
- Large file operations may timeout (30s default)

## Authentication

Currently no authentication required (local network only). For production deployment, implement:
- JWT tokens
- API key authentication
- OAuth2 integration

## Latency Guarantees

- WebSocket latency: < 50ms (local)
- Command processing: 100ms - 5s depending on LLM
- Response broadcast: < 10ms

## Bulk Operations

For sending multiple messages, batch them:

```json
[
  {"command": "send_text", "input": "First message"},
  {"command": "send_text", "input": "Second message"}
]
```

Note: Each message is processed sequentially.

---

For implementation details, see ARCHITECTURE.md
