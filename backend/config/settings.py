"""
Configuration settings for JARVIS Backend
"""
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8765))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# LLM Configuration
LLM_PROVIDER: Literal["groq", "ollama"] = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "neural-chat")

# Whisper Configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
USE_GPU = os.getenv("USE_GPU", "False").lower() == "true"

# Audio Configuration
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1024))
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")
WAKE_WORD_THRESHOLD = float(os.getenv("WAKE_WORD_THRESHOLD", 0.5))

# WhatsApp Automation Configuration
WHATSAPP_HEADLESS = os.getenv("WHATSAPP_HEADLESS", "True").lower() == "true"
WHATSAPP_TIMEOUT = int(os.getenv("WHATSAPP_TIMEOUT", 30))
WHATSAPP_CONTACTS_FILE = os.getenv("WHATSAPP_CONTACTS_FILE", "backend/config/contacts.json")

# Speech Output Configuration
USE_TEXT_TO_SPEECH = os.getenv("USE_TEXT_TO_SPEECH", "True").lower() == "true"
TTS_VOICE = os.getenv("TTS_VOICE", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0")
TTS_SPEED = int(os.getenv("TTS_SPEED", 150))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/jarvis.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# System Commands Configuration
ENABLE_SYSTEM_COMMANDS = os.getenv("ENABLE_SYSTEM_COMMANDS", "True").lower() == "true"
ALLOWED_COMMANDS = ["chrome", "notepad", "explorer", "calculator", "vlc"]

# JARVIS Personality Settings
JARVIS_SYSTEM_PROMPT = """You are JARVIS, a blunt, realistic, and highly professional personal assistant. 
You provide direct, concise, and actionable responses. You don't sugarcoat information. 
You are efficient, intelligent, and always focused on practical solutions. 
When asked to do something, you acknowledge it and execute it without unnecessary pleasantries.
Format your responses as JSON with keys: 'response', 'action', 'action_params'."""

JARVIS_RESPONSE_TIMEOUT = int(os.getenv("JARVIS_RESPONSE_TIMEOUT", 30))

# WebSocket Configuration
WEBSOCKET_MAX_SIZE = int(os.getenv("WEBSOCKET_MAX_SIZE", 10485760))  # 10MB
WEBSOCKET_PING_INTERVAL = int(os.getenv("WEBSOCKET_PING_INTERVAL", 20))
WEBSOCKET_PING_TIMEOUT = int(os.getenv("WEBSOCKET_PING_TIMEOUT", 10))
