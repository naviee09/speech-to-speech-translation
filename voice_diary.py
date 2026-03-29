"""
Voice Assistant Diary - Ask Me Anything
========================================
I built this so I can talk to my diary like a friend.
I ask questions, it answers me with voice.

Just speak - it listens and responds naturally.
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
import re

# ============================================
# MY SETTINGS
# ============================================

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3
SILENCE_LIMIT = 15

# ============================================
# VOICE ASSISTANT DIARY
# ============================================

class VoiceAssistantDiary:
    """
    My voice assistant diary
    I ask questions, it answers with voice
    """
    
    def __init__(self):
        self.journal_file = "my_diary.json"
        self.entries = self.load_entries()
        
        # Voice recognition
        self.recognizer = sr.Recognizer()
        
        # VAD for recording
        self.vad = webrtcvad.Vad(VAD_MODE)
        
        # Audio playback
        pygame.mixer.init()
        
        self.conversation_history = []
        
        print("\n" + "="*50)
        print("🗣️ VOICE ASSISTANT DIARY")
        print("="*50)
        print("Ask me anything about your journal!")
        print("Speak naturally - I'll answer")
        print("="*50)
        
        self.speak("Hello! I'm your voice diary. Ask me anything about your thoughts and memories")
    
    def speak(self, text):
        """Speak the answer"""
        print(f"📢 Diary: {text}")
        
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.music.unload()
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"   (Speaking error: {e})")
    
    def load_entries(self):
        """Load journal entries"""
        try:
            if os.path.exists(self.journal_file):
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_entries(self):
        """Save entries"""
        try:
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def record_voice(self, timeout=10):
        """Record voice for entry"""
        
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
                else:
                    if is_speaking:
                        frames.append(data)
                        silent_frames += 1
                        if silent_frames > SILENCE_LIMIT:
                            break
                
        except:
            pass
        
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        if not frames:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diary_{timestamp}.wav"
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename
    
    def listen_for_question(self):
        """Listen for user's question"""
        print("\n🎤 Listening for your question...")
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                print(f"   You asked: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't catch that. Could you say it again?")
            return None
        except sr.RequestError:
            self.speak("Network issue. Please check your internet connection")
            return None
    
    def add_entry_by_voice(self):
        """Add new entry by voice"""
        
        self.speak("What would you like to call this entry?")
        title = self.listen_for_question()
        
        if not title:
            self.speak("I didn't catch that. Let's try later")
            return
        
        self.speak(f"Title: {title}. Now share your thought. I'll record you")
        time.sleep(1)
        
        audio_file = self.record_voice(timeout=30)
        
        if not audio_file:
            self.speak("I didn't hear anything. Entry not saved")
            return
        
        # Convert to text
        self.speak("Converting your voice to text...")
        
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
        except:
            text = "[Could not convert to text]"
        
        # Save
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
        
        self.speak(f"Saved! You now have {len(self.entries)} thoughts in your diary")
    
    def answer_question(self, question):
        """Answer user's question intelligently"""
        
        question_lower = question.lower()
        
        # ===== GREETINGS =====
        if any(word in question_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            self.speak(f"Hello! How can I help you today? You can ask me anything about your journal")
            return True
        
        # ===== GOODBYE =====
        if any(word in question_lower for word in ['bye', 'goodbye', 'exit', 'quit', 'see you']):
            self.speak("Goodbye! Come back when you have more thoughts to share")
            return False
        
        # ===== ADD ENTRY =====
        if any(word in question_lower for word in ['add', 'new', 'create', 'write', 'save']):
            if any(word in question_lower for word in ['entry', 'thought', 'note', 'memory']):
                self.add_entry_by_voice()
                return True
        
        # ===== HOW MANY =====
        if any(word in question_lower for word in ['how many', 'count', 'number of']):
            count = len(self.entries)
            if count == 0:
                self.speak("Your diary is empty. You haven't added any entries yet")
            elif count == 1:
                self.speak(f"You have 1 entry in your diary")
            else:
                self.speak(f"You have {count} entries in your diary")
            return True
        
        # ===== WHEN DID I WRITE =====
        if any(word in question_lower for word in ['when did', 'what date', 'when']):
            # Try to find entry by title
            for entry in self.entries:
                if entry['title'].lower() in question_lower:
                    self.speak(f"Entry '{entry['title']}' was written on {entry['date']} at {entry['time']}")
                    return True
            
            # Show latest
            if self.entries:
                latest = self.entries[-1]
                self.speak(f"Your most recent entry was on {latest['date']} at {latest['time']}")
                self.speak(f"It was about: {latest['title']}")
            else:
                self.speak("You haven't written any entries yet")
            return True
        
        # ===== WHAT DID I SAY =====
        if any(word in question_lower for word in ['what did', 'what was', 'tell me about']):
            # Find by title
            for entry in self.entries:
                if entry['title'].lower() in question_lower:
                    self.speak(f"Entry '{entry['title']}': {entry['content'][:200]}")
                    if len(entry['content']) > 200:
                        self.speak("That's the first part. Would you like to hear the audio?")
                        response = self.listen_for_question()
                        if response and 'yes' in response:
                            self.play_audio(entry['audio_file'])
                    return True
            
            # If not found, ask which one
            if self.entries:
                self.speak("Which entry would you like to hear?")
                for entry in self.entries[-3:]:
                    self.speak(f"Entry {entry['id']}: {entry['title']} from {entry['date']}")
                return True
            else:
                self.speak("Your diary is empty")
            return True
        
        # ===== SEARCH =====
        if any(word in question_lower for word in ['search', 'find', 'look for']):
            # Extract search term
            words = question_lower.split()
            search_term = None
            for i, word in enumerate(words):
                if word in ['search', 'find', 'look'] and i + 1 < len(words):
                    search_term = words[i + 1]
                    break
            
            if not search_term:
                self.speak("What would you like me to search for?")
                search_term = self.listen_for_question()
            
            if search_term:
                results = []
                for entry in self.entries:
                    if (search_term in entry['title'].lower() or 
                        search_term in entry['content'].lower()):
                        results.append(entry)
                
                if results:
                    self.speak(f"I found {len(results)} entries about {search_term}")
                    for entry in results[:3]:
                        self.speak(f"Entry {entry['id']}: {entry['title']} - {entry['date']}")
                else:
                    self.speak(f"I couldn't find anything about {search_term}")
            return True
        
        # ===== SHOW LATEST =====
        if any(word in question_lower for word in ['latest', 'recent', 'last']):
            if self.entries:
                latest = self.entries[-1]
                self.speak(f"Your latest entry is from {latest['date']}")
                self.speak(f"Title: {latest['title']}")
                self.speak(f"Content: {latest['content'][:150]}")
            else:
                self.speak("Your diary is empty")
            return True
        
        # ===== SHOW ALL TITLES =====
        if any(word in question_lower for word in ['show titles', 'list entries', 'what entries']):
            if not self.entries:
                self.speak("Your diary is empty")
            else:
                self.speak(f"You have {len(self.entries)} entries")
                for entry in self.entries:
                    self.speak(f"Entry {entry['id']}: {entry['title']} - {entry['date']}")
            return True
        
        # ===== DELETE =====
        if 'delete' in question_lower:
            # Find entry number
            numbers = re.findall(r'\d+', question_lower)
            if numbers:
                entry_id = int(numbers[0])
                for i, entry in enumerate(self.entries):
                    if entry['id'] == entry_id:
                        if os.path.exists(entry['audio_file']):
                            try:
                                os.unlink(entry['audio_file'])
                            except:
                                pass
                        del self.entries[i]
                        self.save_entries()
                        self.speak(f"Deleted entry {entry_id}")
                        return True
            self.speak("Which entry number would you like to delete?")
            return True
        
        # ===== HELP =====
        if any(word in question_lower for word in ['help', 'what can', 'what do', 'how to']):
            self.speak("You can ask me things like:")
            self.speak("How many entries do I have?")
            self.speak("What did I say about [topic]?")
            self.speak("Show me my latest entry")
            self.speak("Add a new thought")
            self.speak("Delete entry 3")
            self.speak("Search for something")
            return True
        
        # ===== THANK YOU =====
        if any(word in question_lower for word in ['thank', 'thanks']):
            self.speak("You're welcome! Anything else I can help with?")
            return True
        
        # ===== DEFAULT =====
        self.speak("I'm not sure how to answer that. Try asking about your entries, or say 'help' to see what I can do")
        return True
    
    def play_audio(self, audio_file):
        """Play audio recording"""
        if not os.path.exists(audio_file):
            self.speak("Audio file not found")
            return
        
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self.speak("Playing your recording...")
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except:
            self.speak("Could not play audio")
    
    def run(self):
        """Main loop - listen and answer"""
        
        running = True
        
        while running:
            question = self.listen_for_question()
            
            if question:
                running = self.answer_question(question)
            else:
                # No question detected, wait a bit
                time.sleep(0.5)

# ============================================
# RUN THE VOICE ASSISTANT
# ============================================

if __name__ == "__main__":
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
    
    if missing:
        print("\n❌ Missing some libraries!")
        print(f"   pip install {' '.join(missing)}")
        print("\nThen run again:")
        print("   python voice_diary.py")
    else:
        diary = VoiceAssistantDiary()
        try:
            diary.run()
        except KeyboardInterrupt:
            diary.speak("Goodbye!")
        except Exception as e:
            print(f"Error: {e}")
