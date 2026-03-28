class Config:
    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1

    # VAD settings
    VAD_MODE = 3
    VAD_FRAME_MS = 30

    # Translation settings
    TARGET_LANGUAGE = "en"  # Change to "hi" for Hindi, "es" for Spanish, etc.

    # TTS settings
    TTS_SPEED = 1.0