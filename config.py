import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    FORMAT = 'int16'

    # VAD settings
    VAD_MODE = 3
    VAD_FRAME_MS = 30

    # ASR settings
    ASR_MODEL = "base"  # Change to "tiny" if you have memory issues
    ASR_LANGUAGE = None

    # Translation settings
    TARGET_LANGUAGE = "en"
    TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-mul-en"

    # TTS settings
    TTS_MODEL = "coqui"
    TTS_SPEED = 1.0

    # API Keys (optional - leave empty for local models)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
    AZURE_REGION = os.getenv("AZURE_REGION", "")