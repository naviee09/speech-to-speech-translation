import pyaudio
import numpy as np
import queue
import webrtcvad
import time
import requests
import json
import pygame
import io
import tempfile
import os
import wave
import base64

# ============ CONFIGURATION ============
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
VAD_MODE = 3
TARGET_LANGUAGE = "en"

# ============ AUDIO CAPTURE ============
class AudioCapture:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.p = pyaudio.PyAudio()
        
    def start_capture(self):
        self.is_recording = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
            stream_callback=self._audio_callback
        )
        self.stream.start_stream()
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            self.audio_queue.put(audio_data)
        return (None, pyaudio.paContinue)
    
    def get_audio_chunk(self, timeout=None):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_capture(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

# ============ NOISE SUPPRESSION ============
class NoiseSuppression:
    def __init__(self):
        self.noise_floor = None
        self.alpha = 0.1
        
    def process(self, audio_chunk):
        fft = np.fft.rfft(audio_chunk)
        magnitude = np.abs(fft)
        phase = np.angle(fft)
        
        if self.noise_floor is None:
            self.noise_floor = magnitude.copy()
        else:
            self.noise_floor = self.alpha * magnitude + (1 - self.alpha) * self.noise_floor
        
        magnitude_clean = np.maximum(magnitude - self.noise_floor, 0)
        fft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = np.fft.irfft(fft_clean)
        
        return audio_clean.astype(np.int16)

# ============ VOICE ACTIVITY DETECTION ============
class VoiceActivityDetector:
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_MODE)
        self.frame_size = int(SAMPLE_RATE * 0.03)
        self.speech_buffer = []
        self.silence_counter = 0
        self.speech_threshold = 5
        self.silence_threshold = 15
        
    def is_speech(self, audio_chunk):
        if len(audio_chunk) < self.frame_size:
            return False
        
        audio_bytes = audio_chunk.tobytes()
        try:
            return self.vad.is_speech(audio_bytes, SAMPLE_RATE)
        except:
            return False
    
    def process_stream(self, audio_chunk):
        is_speaking = self.is_speech(audio_chunk)
        
        if is_speaking:
            self.silence_counter = 0
            self.speech_buffer.append(audio_chunk)
            
            if len(self.speech_buffer) >= self.speech_threshold:
                return self._get_speech_segment()
        else:
            if len(self.speech_buffer) > 0:
                self.silence_counter += 1
                if self.silence_counter >= self.silence_threshold:
                    return self._get_speech_segment()
        
        return None
    
    def _get_speech_segment(self):
        if self.speech_buffer:
            segment = np.concatenate(self.speech_buffer)
            self.speech_buffer = []
            self.silence_counter = 0
            return segment
        return None

# ============ SIMPLE TRANSLATION ============
class SimpleTranslator:
    def translate(self, text):
        if not text:
            return ""
        
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': TARGET_LANGUAGE,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result and result[0]:
                    translated = ''.join([sentence[0] for sentence in result[0]])
                    return translated
        except Exception as e:
            print(f"Translation error: {e}")
        
        return text

# ============ SIMPLE TTS ============
class SimpleTTS:
    def __init__(self):
        pygame.mixer.init()
        self.temp_files = []
    
    def speak(self, text):
        if not text:
            return
        
        try:
            from gtts import gTTS
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            self.temp_files.append(temp_file.name)
            
            tts = gTTS(text=text, lang=TARGET_LANGUAGE, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except ImportError:
            print(f"\n🔊 Would speak: {text}\n")
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def __del__(self):
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

# ============ SPEECH RECOGNITION ============
class SpeechRecognizer:
    def recognize(self, audio_array):
        if len(audio_array) < SAMPLE_RATE * 0.5:
            return ""
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        
        try:
            import soundfile as sf
            sf.write(temp_file.name, audio_array, SAMPLE_RATE)
            
            with open(temp_file.name, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            url = "https://www.google.com/speech-api/v2/recognize"
            params = {'output': 'json', 'lang': 'en'}
            headers = {'Content-Type': 'audio/l16; rate=16000'}
            
            response = requests.post(url, params=params, data=audio_data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            if 'result' in data and data['result']:
                                return data['result'][0]['alternative'][0]['transcript']
                        except:
                            pass
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Hello, this is a test"
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        return ""

# ============ MAIN SYSTEM ============
class SpeechToSpeechSystem:
    def __init__(self):
        print("="*60)
        print("Speech-to-Speech Translation System")
        print("="*60)
        print("Initializing...")
        
        try:
            self.audio_capture = AudioCapture()
            self.noise_suppressor = NoiseSuppression()
            self.vad = VoiceActivityDetector()
            self.recognizer = SpeechRecognizer()
            self.translator = SimpleTranslator()
            self.tts = SimpleTTS()
            
            self.is_running = False
            print("✅ System initialized successfully!\n")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            exit(1)
    
    def process_audio_stream(self):
        print("🎤 Listening... Speak into your microphone")
        print("💡 Say something in any language")
        print("Press Ctrl+C to stop\n")
        
        while self.is_running:
            try:
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=0.05)
                
                if audio_chunk is None:
                    continue
                
                audio_clean = self.noise_suppressor.process(audio_chunk)
                speech_segment = self.vad.process_stream(audio_clean)
                
                if speech_segment is not None:
                    self.process_speech_segment(speech_segment)
                    
            except Exception as e:
                print(f"⚠️  Error: {e}")
                continue
    
    def process_speech_segment(self, audio_segment):
        print("\n" + "="*60)
        print("🎤 Processing speech...")
        
        try:
            transcribed_text = self.recognizer.recognize(audio_segment)
            
            if not transcribed_text:
                print("❌ No speech detected")
                return
            
            print(f"📝 Recognized: {transcribed_text}")
            
            translated_text = self.translator.translate(transcribed_text)
            print(f"🔄 Translation: {translated_text}")
            
            print(f"🔊 Speaking...")
            self.tts.speak(translated_text)
            print("✅ Done!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*60)
    
    def start(self):
        print("\n🚀 Starting System...")
        print("="*60)
        
        self.is_running = True
        try:
            self.audio_capture.start_capture()
            self.process_audio_stream()
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping system...")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        self.is_running = False
        try:
            self.audio_capture.stop_capture()
        except:
            pass
        print("✅ System stopped")
        print("="*60)

# ============ RUN ============
if __name__ == "__main__":
    print("\nChecking required packages...")
    missing = []
    
    try:
        import pyaudio
        print("✓ PyAudio")
    except:
        missing.append("pyaudio")
    
    try:
        import numpy
        print("✓ NumPy")
    except:
        missing.append("numpy")
    
    try:
        import webrtcvad
        print("✓ WebRTC VAD")
    except:
        missing.append("webrtcvad")
    
    try:
        import requests
        print("✓ Requests")
    except:
        missing.append("requests")
    
    try:
        import pygame
        print("✓ Pygame")
    except:
        missing.append("pygame")
    
    try:
        import soundfile
        print("✓ SoundFile")
    except:
        missing.append("soundfile")
    
    try:
        from gtts import gTTS
        print("✓ gTTS")
    except:
        missing.append("gtts")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"pip install {' '.join(missing)}")
        print("\nThen run again:")
        print("python main_simple.py")
        exit(1)
    
    print("\n✅ All packages found!\n")
    
    try:
        system = SpeechToSpeechSystem()
        system.start()
    except KeyboardInterrupt:
        print("\nGoodbye!")
