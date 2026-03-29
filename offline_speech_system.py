"""
PROFESSIONAL OFFLINE SPEECH SYSTEM - MY PROJECT
================================================
I built this to work WITHOUT INTERNET!
Now I can use it anywhere - on trains, in remote areas, anywhere.

This is my most advanced project. It took me 3 weeks to get everything working offline.
"""

import os
import json
import wave
import pyaudio
import numpy as np
import threading
import time
from datetime import datetime
import queue
import tempfile
import subprocess
import sys
import webrtcvad

# ============================================
# MY SETTINGS - TUNED FOR OFFLINE USE
# ============================================

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3
SILENCE_LIMIT = 15

# ============================================
# OFFLINE SPEECH RECOGNITION
# I found Vosk after trying 3 different libraries
# It's the only one that works well offline
# ============================================

class MyOfflineSTT:
    """
    This converts my voice to text without internet
    I spent 2 days figuring out how to download the model
    """
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.model_path = "my_speech_model"
        self.init_model()
    
    def init_model(self):
        """Download and setup the offline model"""
        print("\n🔧 Setting up offline speech recognition...")
        
        try:
            from vosk import Model, KaldiRecognizer
            
            if not os.path.exists(self.model_path):
                print("   📥 Downloading speech model (about 40MB)...")
                print("   This happens only once, then it works offline")
                
                import urllib.request
                import zipfile
                
                url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                zip_path = "temp_model.zip"
                
                urllib.request.urlretrieve(url, zip_path)
                print("   ✅ Downloaded!")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(".")
                os.rename("vosk-model-small-en-us-0.15", self.model_path)
                os.remove(zip_path)
                print("   ✅ Model ready!")
            
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
            print("✅ Offline speech recognition ready!")
            
        except ImportError:
            print("   ⚠️ Vosk not installed. Run: pip install vosk")
            self.model = None
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            self.model = None
    
    def recognize(self, audio_file):
        """Convert audio to text - NO INTERNET NEEDED!"""
        if not self.model:
            return "[Offline mode ready]"
        
        try:
            wf = wave.open(audio_file, "rb")
            self.recognizer.AcceptWaveform(wf.readframes(wf.getnframes()))
            result = json.loads(self.recognizer.FinalResult())
            wf.close()
            return result.get("text", "")
        except:
            return "[Could not recognize]"

# ============================================
# OFFLINE TEXT TO SPEECH
# This uses my computer's built-in voices
# No internet, no API calls!
# ============================================

class MyOfflineTTS:
    """
    Makes my computer speak without internet
    I like this because it's instant and works anywhere
    """
    
    def __init__(self):
        self.engine = None
        self.init_engine()
    
    def init_engine(self):
        """Setup the speech engine"""
        print("\n🔧 Setting up offline text-to-speech...")
        
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 0.9)
            
            print("✅ Offline text-to-speech ready!")
            
        except ImportError:
            print("   ⚠️ pyttsx3 not installed. Run: pip install pyttsx3")
            self.engine = None
    
    def speak(self, text):
        """Speak the text - instantly, no internet"""
        if not self.engine:
            print(f"🔊 Would speak: {text}")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except:
            print(f"🔊 Couldn't speak: {text}")
    
    def save_to_file(self, text, filename):
        """Save speech to file"""
        if not self.engine:
            return False
        
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            return True
        except:
            return False

# ============================================
# OFFLINE TRANSLATION
# This was the hardest part to get working
# I tried 3 different models before finding one that works
# ============================================

class MyOfflineTranslator:
    """
    Translates text without internet
    Downloads models once, then works anywhere
    """
    
    def __init__(self):
        self.models = {}
        self.model_path = "translation_models"
        self.init_models()
    
    def init_models(self):
        """Setup translation models"""
        print("\n🔧 Setting up offline translation...")
        
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            self.language_pairs = {
                "en-hi": "Helsinki-NLP/opus-mt-en-hi",
                "hi-en": "Helsinki-NLP/opus-mt-en-hi",
                "en-es": "Helsinki-NLP/opus-mt-en-es",
                "es-en": "Helsinki-NLP/opus-mt-en-es",
                "en-fr": "Helsinki-NLP/opus-mt-en-fr",
                "fr-en": "Helsinki-NLP/opus-mt-en-fr",
            }
            
            for pair, model_name in self.language_pairs.items():
                model_folder = os.path.join(self.model_path, pair.replace("-", "_"))
                
                if not os.path.exists(model_folder):
                    print(f"   📥 Downloading {pair} translation model...")
                    print("   This happens once, then it works offline")
                    
                    tokenizer = MarianTokenizer.from_pretrained(model_name)
                    model = MarianMTModel.from_pretrained(model_name)
                    
                    tokenizer.save_pretrained(model_folder)
                    model.save_pretrained(model_folder)
                    
                    print(f"   ✅ {pair} model ready!")
            
            print("✅ Offline translation ready!")
            
        except ImportError:
            print("   ⚠️ Transformers not installed. Run: pip install transformers torch")
        except Exception as e:
            print(f"   ⚠️ Translation error: {e}")
    
    def translate(self, text, source="auto", target="en"):
        """Translate text offline"""
        if not text:
            return text
        
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            pair = f"en-{target}"
            
            model_folder = os.path.join(self.model_path, pair.replace("-", "_"))
            
            if os.path.exists(model_folder):
                tokenizer = MarianTokenizer.from_pretrained(model_folder)
                model = MarianMTModel.from_pretrained(model_folder)
                
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                translated = model.generate(**inputs)
                result = tokenizer.decode(translated[0], skip_special_tokens=True)
                return result
            
        except Exception as e:
            print(f"   Translation error: {e}")
        
        return text

# ============================================
# VOICE RECORDER WITH VAD
# I improved this over many tests
# ============================================

class MyVoiceRecorder:
    """
    Records my voice automatically
    I spent the most time on this part
    """
    
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.recording_count = 0
        
    def record(self, timeout=30):
        """Record voice until silence"""
        
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
        
        print("   🎤 Recording...")
        
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
                            print("   ⏹️ Stopped")
                            break
                
        except KeyboardInterrupt:
            print("\n   ⏹️ Stopped")
        
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        if not frames:
            print("   ❌ No speech detected")
            return None
        
        self.recording_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

# ============================================
# MY VOICE DIARY
# Stores all my thoughts
# ============================================

class MyVoiceDiary:
    """
    My personal journal that I can update with voice
    """
    
    def __init__(self):
        self.diary_file = "my_diary.json"
        self.entries = self.load_entries()
        self.recorder = MyVoiceRecorder()
        self.stt = MyOfflineSTT()
        
    def load_entries(self):
        try:
            if os.path.exists(self.diary_file):
                with open(self.diary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_entries(self):
        try:
            with open(self.diary_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def add_entry(self):
        print("\n📔 New Diary Entry")
        title = input("Title: ").strip()
        
        if not title:
            print("No title, skipping")
            return
        
        print("\nSpeak your thought...")
        audio_file = self.recorder.record(timeout=30)
        
        if audio_file:
            print("Converting to text...")
            text = self.stt.recognize(audio_file)
            print(f"   Text: {text}")
            
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
            self.save_entries()
            
            print(f"\n✅ Saved! Now have {len(self.entries)} entries")
    
    def show_latest(self):
        if not self.entries:
            print("\n📔 Diary is empty")
            return
        
        latest = self.entries[-1]
        print(f"\n📔 Latest Entry:")
        print(f"   Title: {latest['title']}")
        print(f"   Date: {latest['date']} at {latest['time']}")
        print(f"   Content: {latest['content']}")
        print(f"   Audio: {latest['audio_file']}")
    
    def show_all(self):
        if not self.entries:
            print("\n📔 Diary is empty")
            return
        
        print(f"\n📔 My Diary ({len(self.entries)} entries)")
        print("="*50)
        
        for entry in self.entries:
            print(f"\n[{entry['id']}] {entry['title']}")
            print(f"    {entry['date']} at {entry['time']}")
            print(f"    {entry['content'][:100]}...")
    
    def search(self, keyword):
        results = []
        keyword_lower = keyword.lower()
        
        for entry in self.entries:
            if (keyword_lower in entry['title'].lower() or 
                keyword_lower in entry['content'].lower()):
                results.append(entry)
        
        return results

# ============================================
# MAIN SYSTEM
# ============================================

class MyProfessionalSpeechSystem:
    
    def __init__(self):
        print("\n" + "="*70)
        print("🎙️ MY PROFESSIONAL OFFLINE SPEECH SYSTEM")
        print("="*70)
        print("This is my most advanced project")
        print("Everything works WITHOUT INTERNET!")
        print("="*70)
        
        self.stt = MyOfflineSTT()
        self.tts = MyOfflineTTS()
        self.translator = MyOfflineTranslator()
        self.recorder = MyVoiceRecorder()
        self.diary = MyVoiceDiary()
        
        self.recording_count = 0
        self.translation_count = 0
        
        print("\n✅ All systems ready!")
        print("   I can work anywhere - no internet needed!\n")
        
        self.tts.speak("Hello! I'm your offline speech system. Everything works without internet.")
    
    def speech_to_text(self):
        print("\n🎤 Speech to Text (Offline)")
        print("   Speak clearly...")
        audio_file = self.recorder.record(timeout=10)
        
        if audio_file:
            text = self.stt.recognize(audio_file)
            print(f"\n📝 Text: {text}")
            self.tts.speak(f"You said: {text}")
    
    def text_to_speech(self):
        print("\n🔊 Text to Speech")
        text = input("Enter text to speak: ").strip()
        if text:
            print(f"   Speaking: {text}")
            self.tts.speak(text)
    
    def translate_speech(self):
        print("\n🌐 Speech Translation")
        print("Languages: en (English), hi (Hindi), es (Spanish), fr (French)")
        target = input("Translate to (en/hi/es/fr): ").strip().lower()
        if target not in ['en', 'hi', 'es', 'fr']:
            target = 'en'
        
        print(f"\nSpeak in any language...")
        audio_file = self.recorder.record(timeout=10)
        
        if audio_file:
            original = self.stt.recognize(audio_file)
            print(f"\n📝 Original: {original}")
            translated = self.translator.translate(original, target=target)
            print(f"🌐 Translation: {translated}")
            self.tts.speak(f"Translation: {translated}")
            self.translation_count += 1
    
    def record_voice(self):
        print("\n💾 Voice Recording")
        audio_file = self.recorder.record(timeout=30)
        if audio_file:
            self.recording_count += 1
            print(f"\n✅ Saved: {audio_file}")
    
    def diary_menu(self):
        while True:
            print("\n" + "-"*40)
            print("📔 VOICE DIARY MENU")
            print("-"*40)
            print("1. Add Entry (speak)")
            print("2. Show Latest")
            print("3. Show All")
            print("4. Search")
            print("5. Back to Main")
            print("-"*40)
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.diary.add_entry()
            elif choice == '2':
                self.diary.show_latest()
            elif choice == '3':
                self.diary.show_all()
            elif choice == '4':
                keyword = input("Search for: ").strip()
                if keyword:
                    results = self.diary.search(keyword)
                    if results:
                        print(f"\nFound {len(results)} entries:")
                        for entry in results:
                            print(f"   [{entry['id']}] {entry['title']} - {entry['date']}")
                    else:
                        print("No matches found")
            elif choice == '5':
                break
    
    def show_stats(self):
        print("\n📊 SYSTEM STATISTICS")
        print("="*40)
        print(f"Recordings made: {self.recording_count}")
        print(f"Translations done: {self.translation_count}")
        print(f"Diary entries: {len(self.diary.entries)}")
        
        total_words = 0
        for entry in self.diary.entries:
            total_words += len(entry['content'].split())
        print(f"Total words in diary: {total_words}")
    
    def show_help(self):
        print("\n" + "="*60)
        print("WHAT I CAN DO (OFFLINE)")
        print("="*60)
        print("")
        print("SPEECH FEATURES:")
        print("  1. Speech to Text - Convert your voice to text (offline)")
        print("  2. Text to Speech - I'll speak any text (offline)")
        print("  3. Speech Translation - Translate your voice (offline)")
        print("  4. Voice Recording - Save your voice as audio")
        print("")
        print("DIARY FEATURES:")
        print("  5. Voice Diary - Store your thoughts with voice")
        print("")
        print("OTHER:")
        print("  6. Statistics - See your usage")
        print("  7. Help - Show this menu")
        print("  8. Exit")
        print("")
        print("="*60)
        print("All features work WITHOUT INTERNET!")
        print("="*60)
    
    def run(self):
        while True:
            print("\n" + "="*60)
            print("MAIN MENU - MY OFFLINE SPEECH SYSTEM")
            print("="*60)
            print("1. Speech to Text (offline)")
            print("2. Text to Speech (offline)")
            print("3. Speech Translation (offline)")
            print("4. Voice Recording")
            print("5. Voice Diary")
            print("6. Statistics")
            print("7. Help")
            print("8. Exit")
            print("="*60)
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.speech_to_text()
            elif choice == '2':
                self.text_to_speech()
            elif choice == '3':
                self.translate_speech()
            elif choice == '4':
                self.record_voice()
            elif choice == '5':
                self.diary_menu()
            elif choice == '6':
                self.show_stats()
            elif choice == '7':
                self.show_help()
            elif choice == '8':
                self.tts.speak(f"Goodbye! You made {self.recording_count} recordings and {self.translation_count} translations")
                print("\n👋 Goodbye!")
                break
            else:
                print("Invalid choice")

# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️ MY OFFLINE SPEECH SYSTEM")
    print("="*60)
    print("This system works WITHOUT INTERNET!")
    print("First run will download models (once)")
    print("After that, everything works offline")
    print("="*60)
    
    missing = []
    try:
        import vosk
    except:
        missing.append("vosk")
    try:
        import pyttsx3
    except:
        missing.append("pyttsx3")
    try:
        import transformers
    except:
        missing.append("transformers")
        missing.append("torch")
    
    if missing:
        print("\n📥 Installing required modules...")
        print("This happens only once!")
        for module in missing:
            print(f"   Installing {module}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        print("\n✅ Installation complete!")
        print("   Run again to use the system")
    else:
        system = MyProfessionalSpeechSystem()
        try:
            system.run()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Try running again")
