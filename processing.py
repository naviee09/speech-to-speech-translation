"""
Speech Processing Module
========================
Handles translation, text-to-speech, and processing pipeline
"""

import requests
import tempfile
import os
from gtts import gTTS
import pygame
from config import TARGET_LANGUAGE

class Translator:
    """Translates text between languages"""
    
    def __init__(self):
        self.target_lang = TARGET_LANGUAGE
        self.url = "https://translate.googleapis.com/translate_a/single"
        
    def translate(self, text):
        """Translate text to target language"""
        if not text:
            return ""
        
        try:
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': self.target_lang,
                'dt': 't',
                'q': text
            }
            response = requests.get(self.url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    return ''.join([s[0] for s in data[0]])
        except Exception as e:
            print(f"Translation error: {e}")
        
        return text

class TextToSpeech:
    """Converts text to speech"""
    
    def __init__(self):
        pygame.mixer.init()
        self.target_lang = TARGET_LANGUAGE
        
    def speak(self, text):
        """Convert text to speech and play"""
        if not text:
            return
        
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang=self.target_lang, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
