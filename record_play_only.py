"""
Voice Recorder - Record and Play Without Saving
================================================
Just speak, hear it back immediately. No files saved.
"""

import speech_recognition as sr
import tempfile
import os
from gtts import gTTS
import pygame
import pyaudio
import wave
import threading
import time

# ============================================
# SIMPLE RECORD AND PLAY - NO FILES SAVED
# ============================================

def record_and_play():
    """
    Record your voice and play it back immediately
    No files are saved on your computer
    """
    
    print("="*50)
    print("🎤 VOICE RECORDER - NO FILES SAVED")
    print("="*50)
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\n🔧 Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("\n🎤 Speak now (I'll listen for 5 seconds)...")
            print("   Say something clearly...")
            
            # Listen for speech
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("\n✅ Recording complete!")
            
            # Step 1: Voice to Text
            print("\n📝 Converting your voice to text...")
            text = recognizer.recognize_google(audio)
            print(f"   You said: \"{text}\"")
            
            # Step 2: Text to Speech (temporary - no save)
            print("\n🔊 Converting text to speech...")
            
            # Create temporary file (will be deleted)
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file.name)
            
            # Play it back
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            print("   🔊 Playing back your voice...")
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Clean up - delete temp file
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            
            print("\n✅ Done! No files were saved on your computer")
            
    except sr.WaitTimeoutError:
        print("\n❌ No speech detected. Try again and speak louder.")
    except sr.UnknownValueError:
        print("\n❌ Could not understand what you said. Speak clearly.")
    except sr.RequestError:
        print("\n❌ Network error. Check your internet connection.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

# ============================================
# RECORD, TRANSLATE, PLAY - NO FILES SAVED
# ============================================

def record_translate_play():
    """
    Record, translate to another language, play back
    No files saved
    """
    
    print("="*50)
    print("🎤 RECORD → TRANSLATE → PLAY (No Files)")
    print("="*50)
    
    # Select language
    print("\nChoose translation language:")
    print("1. English")
    print("2. Hindi")
    print("3. Spanish")
    print("4. French")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    lang_map = {'1': 'en', '2': 'hi', '3': 'es', '4': 'fr'}
    target_lang = lang_map.get(choice, 'en')
    
    lang_names = {'en': 'English', 'hi': 'Hindi', 'es': 'Spanish', 'fr': 'French'}
    print(f"\n✅ Will translate to: {lang_names.get(target_lang, 'English')}")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\n🔧 Adjusting for noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("\n🎤 Speak now (5 seconds)...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("\n✅ Recording complete!")
            
            # Voice to Text
            print("\n📝 Converting to text...")
            original_text = recognizer.recognize_google(audio)
            print(f"   You said: \"{original_text}\"")
            
            # Translate
            print(f"\n🌐 Translating to {lang_names.get(target_lang, 'English')}...")
            import requests
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': target_lang,
                'dt': 't',
                'q': original_text
            }
            response = requests.get(url, params=params, timeout=5)
            
            translated_text = original_text
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    translated_text = ''.join([s[0] for s in data[0]])
            
            print(f"   Translated: \"{translated_text}\"")
            
            # Text to Speech
            print("\n🔊 Converting to speech...")
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=translated_text, lang=target_lang, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            print("   🔊 Playing translation...")
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            
            print(f"\n✅ Done! Heard the translation in {lang_names.get(target_lang, 'English')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

# ============================================
# CONTINUOUS LISTEN AND PLAY (Real-time)
# ============================================

def continuous_mode():
    """
    Keep listening and playing back what you say
    No files saved, real-time
    """
    
    print("="*50)
    print("🎤 CONTINUOUS MODE - Real-time")
    print("="*50)
    print("Speak, hear it back. Press Ctrl+C to stop")
    print("="*50)
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\n🔧 Calibrating...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ready! Speak anytime...\n")
            
            while True:
                print("🎤 Listening...", end="\r")
                
                try:
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    
                    print("\n📝 Processing...")
                    text = recognizer.recognize_google(audio)
                    print(f"   You said: \"{text}\"")
                    
                    print("🔊 Playing back...")
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                    temp_file.close()
                    
                    tts = gTTS(text=text, lang='en', slow=False)
                    tts.save(temp_file.name)
                    
                    pygame.mixer.init()
                    pygame.mixer.music.load(temp_file.name)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                    
                    pygame.mixer.quit()
                    os.unlink(temp_file.name)
                    
                    print("   ✅ Done!\n")
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    print("\n   Could not understand, try again\n")
                    continue
                    
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopped by user")

# ============================================
# MAIN MENU
# ============================================

def main():
    """Main menu for voice recorder"""
    
    while True:
        print("\n" + "="*50)
        print("🎙️ VOICE RECORDER - NO FILES SAVED")
        print("="*50)
        print("1. Record and Play Back (Your voice)")
        print("2. Record, Translate, Play Back")
        print("3. Continuous Mode (Keep listening)")
        print("4. Exit")
        print("="*50)
        
        choice = input("\nChoose (1-4): ").strip()
        
        if choice == '1':
            record_and_play()
        elif choice == '2':
            record_translate_play()
        elif choice == '3':
            continuous_mode()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
