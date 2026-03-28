"""
Real-Time Speech Translation System
Voice Input -> Text -> Translation -> Voice Output
"""

import speech_recognition as sr
import requests
import pygame
import tempfile
import os
import time
from gtts import gTTS
import threading

# System Configuration
SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 1.5
TARGET_LANG = "en"  # English default

# Initialize audio player
pygame.mixer.init()

def get_microphone():
    """Get the default microphone"""
    try:
        return sr.Microphone()
    except Exception as e:
        print(f"Microphone error: {e}")
        return None

def calibrate_microphone(recognizer, mic):
    """Adjust for background noise"""
    print("Adjusting for ambient noise...")
    recognizer.adjust_for_ambient_noise(mic, duration=2)
    print("Calibration complete!")

def listen_for_speech(recognizer, mic):
    """Capture speech from microphone"""
    print("\nListening... (speak now)")
    
    try:
        audio = recognizer.listen(mic, timeout=5, phrase_time_limit=10)
        return audio
    except sr.WaitTimeoutError:
        print("No speech detected")
        return None
    except Exception as e:
        print(f"Listening error: {e}")
        return None

def convert_to_text(recognizer, audio):
    """Convert speech to text using Google API"""
    print("Converting speech to text...")
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Network error: {e}")
        return None

def translate_text(text):
    """Translate text to target language"""
    print("Translating...")
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': TARGET_LANG,
            'dt': 't',
            'q': text
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0]:
                translated = ''.join([s[0] for s in data[0]])
                print(f"Translated: {translated}")
                return translated
    except Exception as e:
        print(f"Translation error: {e}")
    
    return text

def speak_text(text):
    """Convert text to speech and play"""
    print("Speaking...")
    
    temp_file = None
    
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        # Generate speech
        tts = gTTS(text=text, lang=TARGET_LANG, slow=False)
        tts.save(temp_file.name)
        
        # Play audio
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()
        
        # Wait for playback
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
            
    except Exception as e:
        print(f"Speech error: {e}")
    finally:
        # Clean up
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass

def process_audio(audio, recognizer):
    """Process audio through the pipeline"""
    if audio is None:
        return
    
    text = convert_to_text(recognizer, audio)
    if text:
        translated = translate_text(text)
        speak_text(translated)
        print("Done!\n")
    else:
        print("Skipping...\n")

def continuous_mode():
    """Run system in continuous mode"""
    recognizer = sr.Recognizer()
    mic = get_microphone()
    
    if not mic:
        print("Microphone not found!")
        return
    
    print("\n" + "="*50)
    print("Continuous Translation Mode")
    print("Speak in any language, get translation in English")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    calibrate_microphone(recognizer, mic)
    
    try:
        while True:
            audio = listen_for_speech(recognizer, mic)
            if audio:
                process_audio(audio, recognizer)
                
    except KeyboardInterrupt:
        print("\nStopping...")

def single_mode():
    """Run system in single-shot mode"""
    recognizer = sr.Recognizer()
    mic = get_microphone()
    
    if not mic:
        print("Microphone not found!")
        return
    
    print("\n" + "="*50)
    print("Single Translation Mode")
    print("="*50)
    
    calibrate_microphone(recognizer, mic)
    
    input("\nPress Enter, then speak...")
    
    audio = listen_for_speech(recognizer, mic)
    if audio:
        process_audio(audio, recognizer)

def test_microphone():
    """Test if microphone is working"""
    print("\nTesting microphone...")
    
    recognizer = sr.Recognizer()
    mic = get_microphone()
    
    if not mic:
        print("Microphone not available!")
        return False
    
    try:
        with mic as source:
            print("Adjusting...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Say something for test...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            text = recognizer.recognize_google(audio)
            print(f"Microphone working! Heard: {text}")
            return True
    except sr.WaitTimeoutError:
        print("No sound detected, but microphone appears connected")
        return True
    except Exception as e:
        print(f"Microphone test failed: {e}")
        return False

def change_language():
    """Change target translation language"""
    global TARGET_LANG
    
    print("\nSelect target language:")
    print("1. English (en)")
    print("2. Hindi (hi)")
    print("3. Spanish (es)")
    print("4. French (fr)")
    print("5. German (de)")
    print("6. Japanese (ja)")
    print("7. Chinese (zh)")
    
    choice = input("\nEnter choice (1-7): ")
    
    languages = {
        '1': 'en', '2': 'hi', '3': 'es',
        '4': 'fr', '5': 'de', '6': 'ja', '7': 'zh'
    }
    
    if choice in languages:
        TARGET_LANG = languages[choice]
        print(f"Target language set to: {TARGET_LANG}")
    else:
        print("Invalid choice, keeping current setting")

def main():
    """Main program loop"""
    print("\n" + "="*50)
    print("REAL-TIME SPEECH TRANSLATION SYSTEM")
    print("="*50)
    print("Voice Input -> Text -> Translation -> Voice Output")
    print("="*50)
    
    while True:
        print("\n" + "-"*50)
        print("MAIN MENU")
        print("-"*50)
        print("1. Continuous Mode (Real-time translation)")
        print("2. Single Mode (One-time translation)")
        print("3. Test Microphone")
        print("4. Change Target Language")
        print("5. Exit")
        print("-"*50)
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            continuous_mode()
        elif choice == '2':
            single_mode()
        elif choice == '3':
            test_microphone()
        elif choice == '4':
            change_language()
        elif choice == '5':
            print("\nThank you for using the system!")
            pygame.mixer.quit()
            break
        else:
            print("Invalid choice, please try again")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSystem stopped by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        pygame.mixer.quit()
