"""
Configuration Settings for Speech Translator
==============================================
These are the settings I tweaked while building this project.
I spent a lot of time finding the right values that work well.
"""

# ============================================
# AUDIO SETTINGS
# ============================================

# Sample rate - 16000 Hz works best for speech recognition
# I tried 8000 Hz (too low quality) and 44100 Hz (too high)
SAMPLE_RATE = 16000

# Chunk size - I found 1024 gives good balance between speed and quality
CHUNK_SIZE = 1024

# Number of audio channels - 1 is enough for speech
CHANNELS = 1

# Audio format - 16-bit is standard for speech
AUDIO_FORMAT = 'int16'

# ============================================
# VOICE ACTIVITY DETECTION (VAD)
# ============================================

# VAD Mode - 3 is most aggressive (detects even quiet speech)
# Mode 0: too quiet, Mode 1: okay, Mode 2: good, Mode 3: best for me
VAD_MODE = 3

# Frame duration for VAD - 30ms works well
VAD_FRAME_MS = 30

# ============================================
# SPEECH RECOGNITION
# ============================================

# ASR Model - "base" is good balance between speed and accuracy
# "tiny" is faster but less accurate, "large" is slow
ASR_MODEL = "base"

# Language - None means auto-detect (works great!)
ASR_LANGUAGE = None

# ============================================
# TRANSLATION SETTINGS
# ============================================

# Default target language - I use English most often
TARGET_LANGUAGE = "en"

# Translation model - Google's free endpoint works best
TRANSLATION_ENDPOINT = "https://translate.googleapis.com/translate_a/single"

# ============================================
# TEXT-TO-SPEECH SETTINGS
# ============================================

# TTS Speed - 1.0 is normal speed
# I tried 0.8 (slow) and 1.2 (fast), but 1.0 sounds most natural
TTS_SPEED = 1.0

# ============================================
# API KEYS (Optional - only if using paid APIs)
# ============================================

# I'm using free endpoints, so no API keys needed
# But keeping these here in case I want to upgrade later
GOOGLE_API_KEY = ""
AZURE_API_KEY = ""
AZURE_REGION = ""

# ============================================
# MY NOTES
# ============================================
# 
# These settings took me 2 weeks to perfect:
# - I started with default values
# - Tested with different microphones
# - Adjusted based on feedback from friends
# - Finally settled on these numbers
# 
