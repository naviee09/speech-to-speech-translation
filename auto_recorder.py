"""
Auto Translator Recorder - With Translation
===========================================
This is an upgrade to my auto recorder.
It not only saves your voice, but also translates it
and saves the translation as audio.

I added this because I wanted to practice languages.
"""

import pyaudio
import wave
import webrtcvad
import numpy as np
import requests
import tempfile
import os
from datetime import datetime
from gtts import gTTS
import speech_recognition as sr

# ============================================
# SETTINGS
# ============================================

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3

class AutoTranslator:
    """
    Records speech, translates, saves both original and translation
    I use Google's free APIs for translation
    """
    
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.frame_size = int(SAMPLE_RATE * 0.03)
        
        self.speech_buffer = []
        self.silence_count = 0
        self.is_speaking = False
        
        self.recordings_made = 0
        
        # Ask user for target language
        print("\n" + "="*50)
        print("🎤 Auto Translator Recorder")
        print("="*50)
        print("I built this to practice foreign languages")
        print("It saves your voice AND the translation")
        print("="*50)
        
        print("\nWhat language do you want to translate to?")
        print("1. English")
        print("2. Hindi")
        print("3. Spanish")
        print("4. French")
        
        choice = input("\nEnter number (1-4): ").strip()
        
        language_map = {
            '1': ('en', 'English'),
            '2': ('hi', 'Hindi'),
            '3': ('es', 'Spanish'),
            '4': ('fr', 'French')
        }
        
        self.target_code, self.target_name = language_map.get(choice, ('en', 'English'))
        print(f"\n✅ Translating to: {self.target_name}\n")
    
    def translate_text(self, text):
        """
        Translate text using Google's free API
        I found this endpoint online - works great without API key
        """
        if not text:
            return text
        
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',  # Auto-detect source language
                'tl': self.target_code,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    # Extract the translated text
                    translated = ''.join([s[0] for s in data[0]])
                    return translated
                    
        except Exception as e:
            print(f"   Translation error: {e}")
        
        return text
    
    def save_audio_with_translation(self, frames):
        """
        Save original voice and translated audio
        This was the hardest part to implement
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 1: Save original voice
        voice_file = f"my_voice_{timestamp}.wav"
        
        try:
            wf = wave.open(voice_file, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print(f"\n💾 Voice saved: {voice_file}")
            
        except Exception as e:
            print(f"   Couldn't save voice: {e}")
            return
        
        # Step 2: Convert voice to text
        print("   Converting speech to text...")
        
        recognizer = sr.Recognizer()
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        
        # Save temporary file for recognition
        wf2 = wave.open(temp_file.name, 'wb')
        wf2.setnchannels(CHANNELS)
        wf2.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf2.setframerate(SAMPLE_RATE)
        wf2.writeframes(b''.join(frames))
        wf2.close()
        
        try:
            with sr.AudioFile(temp_file.name) as source:
                audio = recognizer.record(source)
                original_text = recognizer.recognize_google(audio)
                print(f"   You said: \"{original_text}\"")
                
                # Step 3: Translate
                print(f"   Translating to {self.target_name}...")
                translated_text = self.translate_text(original_text)
                print(f"   Translation: \"{translated_text}\"")
                
                # Step 4: Save translation as audio
                audio_file = f"translation_{timestamp}.mp3"
                tts = gTTS(text=translated_text, lang=self.target_code, slow=False)
                tts.save(audio_file)
                print(f"💾 Translation saved: {audio_file}")
                
                self.recordings_made += 1
                
        except sr.UnknownValueError:
            print("   Couldn't understand - maybe too much background noise?")
        except sr.RequestError:
            print("   Network error - check internet connection")
        except Exception as e:
            print(f"   Error: {e}")
        
        finally:
            # Clean up temp file
            os.unlink(temp_file.name)
    
    def check_for_speech(self, audio_data):
        """Check if audio contains speech"""
        if len(audio_data) < self.frame_size:
            return False
        
        try:
            return self.vad.is_speech(audio_data.tobytes(), SAMPLE_RATE)
        except:
            return False
    
    def process_audio(self, audio_chunk):
        """Process audio and detect speech"""
        
        is_speech = self.check_for_speech(audio_chunk)
        
        if is_speech:
            if not self.is_speaking:
                print("\n🔴 Recording...")
                self.is_speaking = True
                self.speech_buffer = []
                self.silence_count = 0
            
            self.speech_buffer.append(audio_chunk)
            self.silence_count = 0
            
        else:
            if self.is_speaking:
                self.silence_count += 1
                self.speech_buffer.append(audio_chunk)
                
                if self.silence_count > 15:  # ~0.5 seconds silence
                    print("⏹️ Stopped - processing...")
                    self.is_speaking = False
                    
                    if self.speech_buffer:
                        self.save_audio_with_translation(self.speech_buffer)
                    
                    self.speech_buffer = []
                    print("\n🎤 Ready for next recording...")
    
    def run(self):
        """Start the recorder"""
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("\n✅ Ready! Speak in any language")
        print("   It will translate to " + self.target_name)
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                self.process_audio(audio_chunk)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopping...")
            if self.is_speaking and self.speech_buffer:
                self.save_audio_with_translation(self.speech_buffer)
        
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            print(f"\n✅ Done! Saved {self.recordings_made} recordings with translations")

# ============================================
# RUN IT
# ============================================

if __name__ == "__main__":
    # Check dependencies
    missing = []
    try:
        import webrtcvad
    except:
        missing.append("webrtcvad")
    try:
        import gtts
    except:
        missing.append("gtts")
    try:
        import speech_recognition
    except:
        missing.append("SpeechRecognition")
    
    if missing:
        print("\n❌ Missing some libraries!")
        print("   Run this command:")
        print(f"   pip install {' '.join(missing)}")
        print("\nThen run again:")
        print("   python auto_recorder.py")
    else:
        recorder = AutoTranslator()
        recorder.run()
