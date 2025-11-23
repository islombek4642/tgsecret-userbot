"""Configuration module for TgSecret userbot"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3001")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "shared_secret")

# Session configuration
SESSION_STRING = os.getenv("SESSION_STRING", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")

# Storage configuration
BASE_DIR = Path(__file__).parent.parent
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", BASE_DIR / "storage"))
SESSIONS_PATH = BASE_DIR / "sessions"
TEMP_PATH = STORAGE_PATH / "temp"

# Create directories if they don't exist
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
SESSIONS_PATH.mkdir(parents=True, exist_ok=True)
TEMP_PATH.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "userbot.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Rate limiting
MAX_CONCURRENT_DOWNLOADS = 3
DOWNLOAD_TIMEOUT = 300  # 5 minutes
AI_RATE_LIMIT = 10  # requests per minute

# Media settings
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
SUPPORTED_MEDIA_TYPES = {
    'photo': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.webm'],
    'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
}

# AI Provider endpoints
AI_ENDPOINTS = {
    'openai': 'https://api.openai.com/v1/chat/completions',
    'claude': 'https://api.anthropic.com/v1/messages',
    'gemini': 'https://generativelanguage.googleapis.com/v1beta/models',
    'custom': os.getenv("CUSTOM_AI_ENDPOINT", "")
}

# Default AI models
DEFAULT_AI_MODELS = {
    'openai': 'gpt-4-turbo-preview',
    'claude': 'claude-3-opus-20240229',
    'gemini': 'gemini-pro'
}
