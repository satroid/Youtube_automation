import os
import socket
from pathlib import Path
from dotenv import load_dotenv
import imageio_ffmpeg

# Enforce IPv4 resolution on Windows to prevent IPv6 DNS timeouts
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if family == 0 or family == socket.AF_UNSPEC:
        family = socket.AF_INET
    return _orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = _ipv4_getaddrinfo

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
AUDIO_DIR = ASSETS_DIR / "audio"
FONTS_DIR = ASSETS_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Load .env file
load_dotenv(BASE_DIR / ".env")

# API Keys & Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))

# FFmpeg Executable Resolution
try:
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

# Video Configuration
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# Voice Configuration (edge-tts)
DEFAULT_VOICE = "en-US-AnaNeural"
SECONDARY_VOICE = "en-US-EmmaNeural"

# Retention & Sensory Pacing Rules
MAX_STATIC_SCENE_SEC = 4.0
DEFAULT_BPM = 115

# Database
DB_PATH = DATA_DIR / "channel_memory.db"