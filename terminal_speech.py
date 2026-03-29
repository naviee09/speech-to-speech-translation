"""
MY SPEECH SYSTEM - TERMINAL VERSION
====================================
I built this to run completely in terminal/command line.
No browser needed! Everything works with voice.

I spent 4 weeks building this. It does:
1. Speech to Text - Speak, it writes
2. Text to Speech - Type, it speaks  
3. Speech to Speech - Translate voice
4. Voice Recording - Save my voice
5. Voice Diary - Store thoughts
"""

import speech_recognition as sr
import pyaudio
import wave
import webrtcvad
import numpy as np
import os
import json
import tempfile
import time
from datetime import datetime
import requests
from gtts import gTTS
import pygame
import threading

# ============================================
# MY SETTINGS - FOUND THROUGH TESTING
# ============================================

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3
SILENCE_LIMIT = 15

# My diary file
DIARY_FILE = "my_diary.json"
RECORDINGS_FOLDER = "recordings"

# Create recordings folder if needed
if not os.path.exists(RECORDINGS_FOLDER):
    os.makedirs(RECORDINGS_FOLDER)

# ============================================
# MY SPEECH FUNCTIONS
# ============================================

class MySpeechSystem:
    """My complete speech system - terminal version"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.entries = self.load_diary()
        self.recording_count = 0
        self.translation_count = 0
        
        print("\n" + "="*60)
        print("🎙️ MY SPEECH SYSTEM - TERMINAL VERSION")
        print("="*60)
        print("I built this so I can use it without a browser")
        print("Everything works with voice!")
        print("="*60)
    
    # ============================================
    # DIARY FUNCTIONS
    # ============================================
    
    def load_diary(self):
        """Load my saved thoughts"""
        try:
            if os.path.exists(DIARY_FILE):
                with open(DIARY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_diary(self):
        """Save my thoughts"""
        try:
            with open(DIARY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    # ============================================
    # VOICE RECORDING - THE PART I WORKED HARD ON
    # ============================================
    
    def record_voice(self, timeout=10):
        """Record my voice - this took me 2 weeks to get right"""
        
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
        
        print("\n   🎤 Recording... (speak now)")
        
        for _ in range(int(timeout * 1000 / FRAME_MS)):
            data = stream.read(FRAME_SIZE, exception_on_overflow=False)
            is_speech = self.vad.is_speech(data, SAMPLE_RATE)
            
            if is_speech:
                frames.append(data)
                silent_frames = 0
                if not is_speaking:
                    is_speaking = True
                    print("   📝 I hear you...")
            else:
                if is_speaking:
                    frames.append(data)
                    silent_frames += 1
                    if silent_frames > SILENCE_LIMIT:
                        print("   ⏹️ Stopped (you paused)")
                        break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if not frames:
            print("   ❌ I didn't hear anything")
            return None
        
        self.recording_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RECORDINGS_FOLDER}/my_voice_{self.recording_count}_{timestamp}.wav"
        
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
    # SPEECH TO TEXT
    # ============================================
    
    def speech_to_text(self):
        """Convert my voice to text"""
        print("\n🎤 SPEECH TO TEXT")
        print("   I'll listen and convert to text")
        
        audio_file = self.record_voice(timeout=8)
        
        if audio_file:
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio)
                    print(f"\n📝 You said: {text}")
                    return text
            except sr.UnknownValueError:
                print("   Sorry, I couldn't understand")
            except sr.RequestError:
                print("   Network issue - check internet")
        
        return None
    
    # ============================================
    # TEXT TO SPEECH
    # ============================================
    
    def text_to_speech(self):
        """Convert text to speech"""
        print("\n🔊 TEXT TO SPEECH")
        text = input("   Type what you want me to say: ").strip()
        
        if text:
            print(f"   Speaking: {text}")
            self.speak_text(text)
    
    def speak_text(self, text, lang="en"):
        """Speak text - I use gTTS because it sounds natural"""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"   Speech error: {e}")
    
    # ============================================
    # SPEECH TO SPEECH TRANSLATION
    # ============================================
    
    def speech_to_speech(self):
        """Record, translate, speak back"""
        print("\n🌐 SPEECH TO SPEECH TRANSLATION")
        print("   I can translate to:")
        print("   1. English")
        print("   2. Hindi")
        print("   3. Spanish")
        print("   4. French")
        
        choice = input("\n   Choose language (1-4): ").strip()
        
        lang_map = {
            '1': ('en', 'English'),
            '2': ('hi', 'Hindi'),
            '3': ('es', 'Spanish'),
            '4': ('fr', 'French')
        }
        
        lang_code, lang_name = lang_map.get(choice, ('en', 'English'))
        print(f"\n   Translating to: {lang_name}")
        
        print("\n   Speak now...")
        audio_file = self.record_voice(timeout=8)
        
        if audio_file:
            try:
                # Step 1: Speech to text
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    original = recognizer.recognize_google(audio)
                print(f"\n   📝 You said: {original}")
                
                # Step 2: Translate
                translated = self.translate_text(original, lang_code)
                print(f"   🌐 Translation: {translated}")
                
                # Step 3: Speak it
                print("   🔊 Speaking translation...")
                self.speak_text(translated, lang_code)
                self.translation_count += 1
                
            except sr.UnknownValueError:
                print("   Couldn't understand you")
            except sr.RequestError:
                print("   Network error")
    
    def translate_text(self, text, target="en"):
        """Translate text - I found this free endpoint online"""
        if not text:
            return text
        
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': target,
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
    # VOICE RECORDING (Just save)
    # ============================================
    
    def just_record(self):
        """Just record and save my voice"""
        print("\n💾 VOICE RECORDING")
        print("   Speak and I'll save it")
        
        audio_file = self.record_voice(timeout=15)
        
        if audio_file:
            print(f"\n   ✅ Saved: {audio_file}")
            print(f"   You've made {self.recording_count} recordings so far")
    
    # ============================================
    # VOICE DIARY
    # ============================================
    
    def add_diary_entry(self):
        """Add a thought to my diary"""
        print("\n📔 ADD DIARY ENTRY")
        title = input("   Title: ").strip()
        
        if not title:
            print("   No title, skipping")
            return
        
        print("\n   Speak your thought...")
        audio_file = self.record_voice(timeout=20)
        
        if audio_file:
            # Convert to text
            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    content = recognizer.recognize_google(audio)
                print(f"   📝 Your thought: {content}")
            except:
                content = "[Could not convert to text]"
            
            # Save entry
            now = datetime.now()
            entry = {
                "id": len(self.entries) + 1,
                "title": title,
                "content": content,
                "audio_file": audio_file,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S")
            }
            
            self.entries.append(entry)
            self.save_diary()
            
            print(f"\n   ✅ Saved! You have {len(self.entries)} entries now")
    
    def view_diary(self):
        """See my diary entries"""
        if not self.entries:
            print("\n📔 Your diary is empty")
            print("   Add your first thought!")
            return
        
        print("\n📔 MY DIARY")
        print("="*50)
        
        for entry in self.entries[-10:]:  # Show last 10
            print(f"\n[{entry['id']}] {entry['title']}")
            print(f"    📅 {entry['date']} at {entry['time']}")
            print(f"    📝 {entry['content'][:100]}...")
            print(f"    🎵 Audio: {entry['audio_file']}")
    
    def search_diary(self):
        """Search my diary"""
        keyword = input("\n   Search for: ").strip().lower()
        
        if not keyword:
            return
        
        results = []
        for entry in self.entries:
            if (keyword in entry['title'].lower() or 
                keyword in entry['content'].lower()):
                results.append(entry)
        
        if results:
            print(f"\n   Found {len(results)} entries:")
            for entry in results:
                print(f"   [{entry['id']}] {entry['title']} - {entry['date']}")
        else:
            print(f"   No entries found for '{keyword}'")
    
    # ============================================
    # STATS
    # ============================================
    
    def show_stats(self):
        """Show my statistics"""
        print("\n📊 MY STATISTICS")
        print("="*40)
        print(f"   Recordings made: {self.recording_count}")
        print(f"   Translations done: {self.translation_count}")
        print(f"   Diary entries: {len(self.entries)}")
        
        # Total words in diary
        total_words = 0
        for entry in self.entries:
            total_words += len(entry['content'].split())
        print(f"   Words written: {total_words}")
    
    # ============================================
    # HELP
    # ============================================
    
    def show_help(self):
        """Show what I can do"""
        print("\n" + "="*60)
        print("WHAT I CAN DO")
        print("="*60)
        print("")
        print("1. Speech to Text - Speak, I'll write it")
        print("2. Text to Speech - Type, I'll speak it")
        print("3. Speech to Speech - Translate your voice")
        print("4. Voice Recording - Save your voice")
        print("5. Add Diary Entry - Save your thoughts")
        print("6. View Diary - Read your entries")
        print("7. Search Diary - Find old thoughts")
        print("8. Statistics - See your usage")
        print("9. Help - Show this menu")
        print("0. Exit")
        print("")
        print("="*60)
    
    # ============================================
    # MAIN MENU
    # ============================================
    
    def run(self):
        """Main menu loop"""
        
        while True:
            print("\n" + "="*60)
            print("MY SPEECH SYSTEM - TERMINAL")
            print("="*60)
            print("1. 🎤 Speech to Text")
            print("2. 🔊 Text to Speech")
            print("3. 🌐 Speech to Speech Translation")
            print("4. 💾 Voice Recording")
            print("5. 📔 Add Diary Entry")
            print("6. 📖 View Diary")
            print("7. 🔍 Search Diary")
            print("8. 📊 Statistics")
            print("9. ❓ Help")
            print("0. 🚪 Exit")
            print("="*60)
            
            choice = input("\nWhat would you like to do? ").strip()
            
            if choice == '1':
                self.speech_to_text()
            elif choice == '2':
                self.text_to_speech()
            elif choice == '3':
                self.speech_to_speech()
            elif choice == '4':
                self.just_record()
            elif choice == '5':
                self.add_diary_entry()
            elif choice == '6':
                self.view_diary()
            elif choice == '7':
                self.search_diary()
            elif choice == '8':
                self.show_stats()
            elif choice == '9':
                self.show_help()
            elif choice == '0':
                print("\n👋 Goodbye!")
                print(f"   You made {self.recording_count} recordings")
                print(f"   You translated {self.translation_count} times")
                print(f"   You have {len(self.entries)} diary entries")
                print("\n   Come back soon!")
                break
            else:
                print("   Not sure what that means. Type 9 for help")

# ============================================
# RUN MY SYSTEM
# ============================================

if __name__ == "__main__":
    # Check if we have everything
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
        import pygame
    except:
        missing.append("pygame")
    try:
        import requests
    except:
        missing.append("requests")
    
    if missing:
        print("\n" + "="*60)
        print("📦 INSTALLING REQUIRED PACKAGES")
        print("="*60)
        print("This happens only once!")
        for module in missing:
            print(f"   Installing {module}...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        print("\n✅ All packages installed!")
        print("   Run again to use the system")
        print("="*60)
    else:
        system = MySpeechSystem()
        try:
            system.run()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("   Try running again")
