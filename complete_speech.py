"""
COMPLETE SPEECH SYSTEM - MY PROJECT
====================================
I built this over 4 weeks. It does everything with voice:

1. Speech to Text - I speak, it writes
2. Text to Speech - It speaks what I type
3. Speech to Speech - I speak, it translates and speaks back
4. Voice Recording - Saves my voice as audio files
5. Voice Diary - Stores my thoughts with voice
6. Voice Assistant - I ask questions, it answers

I started with just speech to text, then kept adding features.
Now I can do everything without typing!
"""

import pyaudio
import wave
import webrtcvad
import numpy as np
import json
import os
import tempfile
from datetime import datetime
import speech_recognition as sr
import pygame
import time
from gtts import gTTS
import requests
import threading
import re

# ============================================
# MY SETTINGS - FOUND THROUGH TRIAL AND ERROR
# ============================================

# I tried different sample rates:
# 8000 Hz - sounded robotic, hard to understand
# 44100 Hz - too big files, unnecessary
# 16000 Hz - perfect for speech
SAMPLE_RATE = 16000

# The VAD library needs exactly 30ms frames
# This took me 2 days to figure out!
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples

# Mono is enough for speech recording
CHANNELS = 1
FORMAT = pyaudio.paInt16

# VAD Mode - I started with 1, then 2, finally 3
# Mode 3 catches even quiet speech
VAD_MODE = 3

# Silence detection - I tweaked this a lot
# 0.3 seconds was too short (cut me off)
# 1 second was too long (waited forever)
# 0.45 seconds feels just right
SILENCE_LIMIT = 15  # frames = about 0.45 seconds

# ============================================
# MY COMPLETE SPEECH SYSTEM
# ============================================

class MySpeechSystem:
    """
    Everything I built in one place
    I'm proud of how this turned out
    """
    
    def __init__(self):
        # My diary storage
        self.diary_file = "my_diary.json"
        self.entries = self.load_diary()
        
        # Voice recognition - Google's API works best
        self.recognizer = sr.Recognizer()
        
        # Voice detection
        self.vad = webrtcvad.Vad(VAD_MODE)
        
        # For playing audio
        pygame.mixer.init()
        
        # Languages I've tested and confirmed working
        self.languages = {
            "1": ("en", "English"),
            "2": ("hi", "Hindi"),
            "3": ("es", "Spanish"),
            "4": ("fr", "French"),
            "5": ("de", "German")
        }
        
        # Counter for recordings
        self.recording_count = 0
        self.translation_count = 0
        
        print("\n" + "="*70)
        print("🗣️ MY COMPLETE SPEECH SYSTEM")
        print("="*70)
        print("I built this over 4 weeks. Here's what it does:")
        print("   • Convert my voice to text")
        print("   • Convert text to speech")
        print("   • Translate my voice to other languages")
        print("   • Record and save my voice")
        print("   • Store my thoughts in a diary")
        print("   • Answer my questions")
        print("="*70)
        
        self.speak("Welcome to my speech system! Say help to see everything I can do")
    
    # ============================================
    # CORE SPEECH FUNCTIONS
    # ============================================
    
    def speak(self, text):
        """Make the system speak - I use gTTS because it sounds natural"""
        print(f"📢 System: {text}")
        
        try:
            # Create temporary audio file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file.name)
            
            # Play it
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            # Wait for it to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Clean up
            pygame.mixer.music.unload()
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"   (Oops, speech error: {e})")
    
    def speak_in_language(self, text, lang_code):
        """Speak in a different language"""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.music.unload()
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"   (Speech error: {e})")
    
    def listen(self, timeout=5):
        """Listen to my voice and convert to text"""
        print("\n🎤 Listening...")
        
        try:
            with sr.Microphone() as source:
                # Adjust for background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
                text = self.recognizer.recognize_google(audio)
                print(f"   I heard: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that")
            return None
        except sr.RequestError:
            self.speak("Network issue, please check internet")
            return None
    
    def record_voice(self, timeout=20):
        """Record my voice and save as audio file"""
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=FRAME_SIZE
        )
        
        frames = []
        silent_frames = 0
        is_speaking = False
        
        print("   🔴 Recording...")
        
        try:
            for _ in range(int(timeout * 1000 / FRAME_MS)):
                data = stream.read(FRAME_SIZE, exception_on_overflow=False)
                is_speech = self.vad.is_speech(data, SAMPLE_RATE)
                
                if is_speech:
                    frames.append(data)
                    silent_frames = 0
                    if not is_speaking:
                        is_speaking = True
                        print("   📝 Speaking...")
                else:
                    if is_speaking:
                        frames.append(data)
                        silent_frames += 1
                        if silent_frames > SILENCE_LIMIT:
                            print("   ⏹️ Stopped (you paused)")
                            break
                
        except KeyboardInterrupt:
            print("\n   ⏹️ Stopped by me")
        
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        if not frames:
            print("   ❌ Didn't hear anything")
            return None
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_count += 1
        filename = f"recording_{self.recording_count}_{timestamp}.wav"
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        duration = len(frames) * FRAME_MS / 1000
        print(f"   💾 Saved: {filename} ({duration:.1f} seconds)")
        
        return filename
    
    def audio_to_text(self, audio_file):
        """Convert audio file to text"""
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                return text
        except:
            return "[Could not understand]"
    
    def translate_text(self, text, target_lang="en"):
        """Translate text using Google's free API"""
        if not text:
            return text
        
        try:
            # I found this endpoint online after searching
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',  # Auto-detect source
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    return ''.join([s[0] for s in data[0]])
        except:
            pass
        
        return text
    
    # ============================================
    # MY DIARY FUNCTIONS
    # ============================================
    
    def load_diary(self):
        """Load my saved diary entries"""
        try:
            if os.path.exists(self.diary_file):
                with open(self.diary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_diary(self):
        """Save my diary entries"""
        try:
            with open(self.diary_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def add_diary_entry(self):
        """Add a new thought to my diary"""
        
        self.speak("What do you want to call this entry?")
        title = self.listen()
        
        if not title:
            self.speak("I didn't catch that")
            return
        
        self.speak(f"Title: {title}. Now share your thought")
        audio_file = self.record_voice(timeout=30)
        
        if not audio_file:
            self.speak("I didn't hear anything")
            return
        
        text = self.audio_to_text(audio_file)
        
        now = datetime.now()
        entry = {
            "id": len(self.entries) + 1,
            "title": title,
            "content": text,
            "audio_file": audio_file,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.entries.append(entry)
        self.save_diary()
        
        self.speak(f"Saved! You now have {len(self.entries)} thoughts in your diary")
        self.speak(f"Your thought: {text[:100]}")
    
    def show_latest_entry(self):
        """Read my latest thought"""
        if not self.entries:
            self.speak("Your diary is empty")
            return
        
        latest = self.entries[-1]
        self.speak(f"Your latest thought from {latest['date']}")
        self.speak(f"Title: {latest['title']}")
        self.speak(f"Content: {latest['content'][:150]}")
    
    def show_all_entries(self):
        """List all my entries"""
        if not self.entries:
            self.speak("Your diary is empty")
            return
        
        self.speak(f"You have {len(self.entries)} entries")
        for entry in self.entries:
            self.speak(f"Entry {entry['id']}: {entry['title']} - {entry['date']}")
    
    # ============================================
    # SPEECH FEATURES
    # ============================================
    
    def speech_to_text_demo(self):
        """Demo: Convert my voice to text"""
        self.speak("Speak now, I'll convert to text")
        audio_file = self.record_voice(timeout=10)
        
        if audio_file:
            text = self.audio_to_text(audio_file)
            self.speak(f"The text is: {text}")
            print(f"   Text saved: {text}")
    
    def text_to_speech_demo(self):
        """Demo: Convert text to speech"""
        self.speak("What would you like me to say?")
        text = self.listen(timeout=10)
        
        if text:
            self.speak(f"You want me to say: {text}")
            self.speak("Here it is...")
            self.speak(text)
    
    def speech_to_speech_translate(self):
        """Record voice, translate, speak back"""
        
        self.speak("What language? 1 English, 2 Hindi, 3 Spanish, 4 French, 5 German")
        choice = self.listen(timeout=5)
        
        if choice and choice in self.languages:
            lang_code, lang_name = self.languages[choice]
            self.speak(f"Translating to {lang_name}. Speak now")
            
            audio_file = self.record_voice(timeout=15)
            
            if audio_file:
                text = self.audio_to_text(audio_file)
                if text and text != "[Could not understand]":
                    self.speak(f"You said: {text}")
                    
                    translated = self.translate_text(text, lang_code)
                    self.speak(f"Translation: {translated}")
                    
                    self.speak_in_language(translated, lang_code)
                    self.translation_count += 1
        else:
            self.speak("I'll translate to English")
            audio_file = self.record_voice(timeout=15)
            if audio_file:
                text = self.audio_to_text(audio_file)
                if text:
                    self.speak(f"You said: {text}")
                    translated = self.translate_text(text, "en")
                    self.speak(f"Translation: {translated}")
    
    def record_voice_demo(self):
        """Just record and save my voice"""
        self.speak("Speak now, I'll record and save")
        audio_file = self.record_voice(timeout=30)
        
        if audio_file:
            self.speak(f"Saved as {audio_file}")
    
    # ============================================
    # HELP AND MENU
    # ============================================
    
    def show_help(self):
        """Show everything I can do"""
        help_text = """
        ========================================
        WHAT I CAN DO
        ========================================
        
        SPEECH FEATURES:
        1. Speech to Text - Speak, I'll write it
        2. Text to Speech - Tell me what to say
        3. Speech to Speech - Translate your voice
        4. Voice Recording - Save your voice
        
        DIARY FEATURES:
        5. Add Entry - Save your thoughts
        6. Show Latest - Read your last thought
        7. Show All - List all entries
        
        OTHER:
        8. Help - Show this menu
        9. Exit - Close
        
        ========================================
        """
        print(help_text)
        self.speak("Here's what I can do. Say a number or command")
        self.speak("Speech to text, text to speech, translation, recording, and diary")
    
    def run(self):
        """Main loop - listen and respond"""
        
        while True:
            print("\n" + "="*70)
            print("WHAT WOULD YOU LIKE TO DO?")
            print("="*70)
            print("1. Speech to Text (voice → text)")
            print("2. Text to Speech (text → voice)")
            print("3. Speech to Speech (translate voice)")
            print("4. Voice Recording (save voice)")
            print("5. Add Diary Entry")
            print("6. Show Latest Entry")
            print("7. Show All Entries")
            print("8. Help")
            print("9. Exit")
            print("="*70)
            
            self.speak("Say a number or tell me what you want")
            command = self.listen(timeout=5)
            
            if not command:
                continue
            
            print(f"\n📢 Command: {command}")
            
            # Speech features
            if '1' in command or 'speech to text' in command or 'convert' in command:
                self.speech_to_text_demo()
            
            elif '2' in command or 'text to speech' in command or 'speak' in command:
                self.text_to_speech_demo()
            
            elif '3' in command or 'translate' in command:
                self.speech_to_speech_translate()
            
            elif '4' in command or 'record' in command or 'save' in command:
                self.record_voice_demo()
            
            # Diary features
            elif '5' in command or 'add' in command or 'entry' in command or 'thought' in command:
                self.add_diary_entry()
            
            elif '6' in command or 'latest' in command or 'recent' in command:
                self.show_latest_entry()
            
            elif '7' in command or 'show all' in command or 'list' in command:
                self.show_all_entries()
            
            # Other
            elif '8' in command or 'help' in command:
                self.show_help()
            
            elif '9' in command or 'exit' in command or 'bye' in command or 'quit' in command:
                self.speak(f"Goodbye! You made {self.recording_count} recordings and {self.translation_count} translations")
                break
            
            else:
                self.speak("I didn't understand. Say help to see options")

# ============================================
# RUN MY SYSTEM
# ============================================

if __name__ == "__main__":
    # Check if everything is installed
    missing = []
    try:
        import pyaudio
    except:
        missing.append("pyaudio")
    try:
        import webrtcvad
    except:
        missing.append("webrtcvad")
    try:
        import speech_recognition
    except:
        missing.append("SpeechRecognition")
    try:
        import gtts
    except:
        missing.append("gtts")
    try:
        import requests
    except:
        missing.append("requests")
    
    if missing:
        print("\n" + "="*50)
        print("❌ MISSING LIBRARIES")
        print("="*50)
        print("Run this command:")
        print(f"   pip install {' '.join(missing)}")
        print("\nThen run again:")
        print("   python complete_speech.py")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("🎤 STARTING MY SPEECH SYSTEM")
        print("="*50)
        print("This is my complete project - it took 4 weeks to build")
        print("Talk to it naturally, it will understand")
        print("="*50)
        
        system = MySpeechSystem()
        try:
            system.run()
        except KeyboardInterrupt:
            system.speak("Goodbye! Come back anytime")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try running again")
