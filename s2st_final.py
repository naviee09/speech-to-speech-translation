"""
SPEECH-TO-SPEECH TRANSLATION SYSTEM
For Hackathon/Placement Drive
Real-time voice translation with Google APIs
"""

import speech_recognition as sr
import requests
import pygame
import tempfile
import os
import time
from gtts import gTTS
import threading
import queue

print("="*70)
print("🎙️  SPEECH-TO-SPEECH TRANSLATION SYSTEM")
print("="*70)
print("Developed for Hackathon/Placement Drive")
print("="*70)

# Configuration
SOURCE_LANGUAGE = "auto"  # Auto-detect
TARGET_LANGUAGE = "en"    # Translate to English (change to "hi" for Hindi, "es" for Spanish)
SILENCE_TIMEOUT = 1.5     # Seconds of silence to stop recording

class SpeechToSpeechSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_running = True
        self.temp_files = []
        
        # Configure recognizer
        self.recognizer.energy_threshold = 3000  # Sensitivity
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Test microphone
        if not self.test_microphone():
            print("\n❌ Microphone not detected!")
            print("\nTroubleshooting:")
            print("1. Make sure microphone is plugged in")
            print("2. Check Windows Settings → Privacy → Microphone")
            print("3. Allow apps to access your microphone")
            exit(1)
    
    def test_microphone(self):
        """Test if microphone is working"""
        print("\n🔍 Testing microphone...")
        try:
            with sr.Microphone() as source:
                print("   Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("   Listening for test (say something)...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio)
                print(f"   ✅ Microphone working! Test: '{text}'")
                return True
        except sr.WaitTimeoutError:
            print("   ⚠️  No speech detected, but microphone is active")
            return True
        except Exception as e:
            print(f"   ❌ Microphone error: {e}")
            return False
    
    def translate_text(self, text):
        """Translate text using Google Translate"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': SOURCE_LANGUAGE,
                'tl': TARGET_LANGUAGE,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result and result[0]:
                    translated = ''.join([s[0] for s in result[0]])
                    return translated
        except Exception as e:
            print(f"   Translation error: {e}")
        return text
    
    def speak_text(self, text):
        """Convert text to speech and play it"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            self.temp_files.append(temp_file.name)
            
            # Generate speech
            tts = gTTS(text=text, lang=TARGET_LANGUAGE, slow=False)
            tts.save(temp_file.name)
            
            # Play audio
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
        except Exception as e:
            print(f"   Speech error: {e}")
            return False
    
    def process_speech(self, audio):
        """Process speech: recognize, translate, and speak"""
        print("\n" + "="*70)
        print("🎤 Processing...")
        
        try:
            # Step 1: Recognize speech
            print("   📝 Recognizing speech...")
            original_text = self.recognizer.recognize_google(audio)
            print(f"   ✅ Original: {original_text}")
            
            # Step 2: Translate
            print("   🌐 Translating...")
            translated_text = self.translate_text(original_text)
            print(f"   ✅ Translation: {translated_text}")
            
            # Step 3: Speak translation
            print("   🔊 Speaking translation...")
            self.speak_text(translated_text)
            print("   ✅ Done!")
            
            return True
            
        except sr.UnknownValueError:
            print("   ❌ Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"   ❌ Network error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def listen_continuous(self):
        """Continuous listening mode"""
        print("\n" + "="*70)
        print("🎤 READY FOR VOICE INPUT")
        print("="*70)
        print("\nInstructions:")
        print("   • Speak clearly into your microphone")
        print("   • The system will automatically detect when you finish speaking")
        print("   • Press Ctrl+C to stop\n")
        print("="*70)
        
        try:
            with sr.Microphone() as source:
                # Calibrate
                print("🔧 Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("✅ Ready! Speak now...\n")
                
                while self.is_running:
                    print("🎤 Listening...", end=" ", flush=True)
                    
                    try:
                        # Listen for speech
                        audio = self.recognizer.listen(
                            source, 
                            timeout=5, 
                            phrase_time_limit=15
                        )
                        print("speech detected!")
                        
                        # Process in separate thread
                        thread = threading.Thread(
                            target=self.process_speech, 
                            args=(audio,)
                        )
                        thread.start()
                        
                    except sr.WaitTimeoutError:
                        print("no speech", end="\r", flush=True)
                        continue
                        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping system...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def listen_once(self):
        """Single recording mode"""
        print("\n" + "="*70)
        print("🎤 ONE-TIME RECORDING MODE")
        print("="*70)
        
        try:
            with sr.Microphone() as source:
                print("\n🔧 Calibrating...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                input("\nPress Enter and then speak...")
                
                print("🎤 Recording... (speak now)")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                
                self.process_speech(audio)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def cleanup(self):
        """Clean up temporary files"""
        for file in self.temp_files:
            try:
                os.unlink(file)
            except:
                pass
    
    def run(self):
        """Main menu"""
        while True:
            print("\n" + "="*70)
            print("MAIN MENU")
            print("="*70)
            print("1. Continuous Voice Translation (Real-time)")
            print("2. One-time Recording (Press Enter to start)")
            print("3. Change Target Language")
            print("4. Test Microphone")
            print("5. Exit")
            print("="*70)
            
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                self.listen_continuous()
            elif choice == '2':
                self.listen_once()
            elif choice == '3':
                print("\nAvailable languages:")
                print("  en - English")
                print("  hi - Hindi")
                print("  es - Spanish")
                print("  fr - French")
                print("  de - German")
                print("  zh - Chinese")
                print("  ja - Japanese")
                print("  ar - Arabic")
                print("  ru - Russian")
                
                lang = input("\nEnter language code (default: en): ").strip().lower()
                if lang:
                    global TARGET_LANGUAGE
                    TARGET_LANGUAGE = lang
                    print(f"✅ Target language set to: {lang}")
                else:
                    print("✅ Keeping English as target")
                    
            elif choice == '4':
                self.test_microphone()
            elif choice == '5':
                print("\n👋 Goodbye!")
                self.cleanup()
                break
            else:
                print("❌ Invalid choice")

# Main execution
if __name__ == "__main__":
    try:
        system = SpeechToSpeechSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        pygame.mixer.quit()
