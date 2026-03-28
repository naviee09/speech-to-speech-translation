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

def test_microphone():
    """Test if microphone is working"""
    print("\nTesting microphone...")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Say something for test...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            text = recognizer.recognize_google(audio)
            print(f"✅ Microphone working! Heard: {text}")
            return True
    except sr.WaitTimeoutError:
        print("⚠️ No sound detected, but microphone appears connected")
        return True
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if microphone is plugged in")
        print("2. Windows Settings -> Privacy -> Microphone -> Allow access")
        return False

def translate_text(text):
    """Translate text to target language"""
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
                return translated
    except Exception as e:
        print(f"Translation error: {e}")
    
    return text

def speak_text(text):
    """Convert text to speech and play"""
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

def continuous_mode():
    """Run system in continuous mode"""
    print("\n" + "="*50)
    print("Continuous Translation Mode")
    print("Speak in any language, get translation in English")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ready! Speak now...\n")
            
            while True:
                print("🎤 Listening...", end=" ", flush=True)
                
                try:
                    # Listen for speech
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    print("speech detected!")
                    
                    # Convert to text
                    print("   Converting to text...")
                    text = recognizer.recognize_google(audio)
                    print(f"   📝 Original: {text}")
                    
                    # Translate
                    print("   Translating...")
                    translated = translate_text(text)
                    print(f"   🌐 Translation: {translated}")
                    
                    # Speak
                    print("   Speaking...")
                    speak_text(translated)
                    print("   ✅ Done!\n")
                    
                except sr.WaitTimeoutError:
                    print("no speech", end="\r", flush=True)
                    continue
                except sr.UnknownValueError:
                    print("could not understand", end="\r", flush=True)
                    continue
                except sr.RequestError as e:
                    print(f"\n   Network error: {e}")
                    continue
                    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

def single_mode():
    """Run system in single-shot mode"""
    print("\n" + "="*50)
    print("Single Translation Mode")
    print("="*50)
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            input("\nPress Enter, then speak...")
            
            print("🎤 Recording...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # Convert to text
            print("Converting to text...")
            text = recognizer.recognize_google(audio)
            print(f"\n📝 Original: {text}")
            
            # Translate
            print("Translating...")
            translated = translate_text(text)
            print(f"🌐 Translation: {translated}")
            
            # Speak
            print("Speaking...")
            speak_text(translated)
            print("✅ Done!\n")
            
    except sr.WaitTimeoutError:
        print("No speech detected")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Error: {e}")

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
    print("8. Arabic (ar)")
    print("9. Russian (ru)")
    
    choice = input("\nEnter choice (1-9): ").strip()
    
    languages = {
        '1': 'en', '2': 'hi', '3': 'es', '4': 'fr', '5': 'de',
        '6': 'ja', '7': 'zh', '8': 'ar', '9': 'ru'
    }
    
    if choice in languages:
        TARGET_LANG = languages[choice]
        print(f"✅ Target language set to: {TARGET_LANG}")
    else:
        print("❌ Invalid choice, keeping current setting")

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
