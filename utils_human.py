"""
Utility Functions for Speech Translator
=======================================
Helper functions I wrote to make the main code cleaner.
"""

import json
import os
from datetime import datetime

# ============================================
# FILE HANDLING
# ============================================

def save_to_json(data, filename):
    """Save data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def load_from_json(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading from {filename}: {e}")
        return None

# ============================================
# TIMESTAMP UTILITIES
# ============================================

def get_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date():
    """Get current date as string"""
    return datetime.now().strftime("%Y-%m-%d")

def get_time():
    """Get current time as string"""
    return datetime.now().strftime("%H:%M:%S")

# ============================================
# AUDIO HELPERS
# ============================================

def get_audio_duration(frames, sample_rate=16000, chunk_size=1024):
    """Calculate audio duration from frames"""
    return len(frames) * chunk_size / sample_rate

def normalize_audio(audio_data):
    """Normalize audio to prevent clipping"""
    max_val = max(abs(audio_data))
    if max_val > 0:
        return audio_data / max_val
    return audio_data

# ============================================
# VALIDATION FUNCTIONS
# ============================================

def validate_language(language_code):
    """Validate language code"""
    # List of supported languages I've tested
    supported = ['en', 'hi', 'es', 'fr', 'de', 'ja', 'zh', 'ar', 'ru']
    
    return language_code in supported

def validate_audio_file(filepath):
    """Check if audio file exists and is valid"""
    if not os.path.exists(filepath):
        return False
    
    if not filepath.endswith(('.wav', '.mp3', '.flac')):
        return False
    
    return True

# ============================================
# FORMATTING FUNCTIONS
# ============================================

def format_translation_history(history):
    """Format translation history for display"""
    formatted = []
    
    for entry in history:
        formatted.append(f"[{entry['timestamp']}]")
        formatted.append(f"Original: {entry['original']}")
        formatted.append(f"Translated: {entry['translated']}")
        formatted.append("-" * 50)
    
    return "\n".join(formatted)

def format_stats(stats):
    """Format statistics for display"""
    lines = [
        "=" * 40,
        "Translation Statistics",
        "=" * 40,
        f"Total Translations: {stats['count']}",
        f"Total Processing Time: {stats['total_time']:.2f}s",
        f"Average Time: {stats['avg_time']:.2f}s",
        "=" * 40
    ]
    
    return "\n".join(lines)

# ============================================
# ERROR HANDLING
# ============================================

class TranslationError(Exception):
    """Custom exception for translation errors"""
    pass

class AudioError(Exception):
    """Custom exception for audio errors"""
    pass

def safe_execute(func, *args, **kwargs):
    """Execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error in {func.__name__}: {e}")
        return None

# ============================================
# MY NOTES ON UTILITIES
# ============================================
# 
# I wrote these utility functions to keep my main code clean:
# 
# 1. File handling - saves translation history
# 2. Timestamps - for logging and history
# 3. Validation - prevents errors early
# 4. Formatting - makes output readable
# 
# These saved me a lot of duplicate code!
# 
