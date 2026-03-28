import pyaudio
import numpy as np
import queue
import webrtcvad
import time
import requests
import json
from gtts import gTTS
import pygame
import io
import tempfile
import os

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


# ============ LANGUAGE IDENTIFICATION ============
class LanguageIdentifier:
    def identify(self, text):
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': 'en',
                'dt': 't',
                'q': text[:100]
            }
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                # The language code is in the response
                return 'detected', 0.8
        except:
            pass
        return 'en', 0.5


# ============ SPEECH RECOGNITION ============
class SpeechRecognizer:
    def transcribe(self, audio_array):
        if len(audio_array) < SAMPLE_RATE * 0.5:
            return ""

        # Save to temporary WAV file
        import soundfile as sf
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        sf.write(temp_file.name, audio_array, SAMPLE_RATE)

        try:
            # Use Google Speech Recognition (free, no API key needed)
            import speech_recognition as sr
            recognizer = sr.Recognizer()

            with sr.AudioFile(temp_file.name) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                return text
        except ImportError:
            # Fallback to a simple message
            return "[Speech detected]"
        except Exception as e:
            return ""
        finally:
            os.unlink(temp_file.name)


# ============ TRANSLATION ============
class TranslationEngine:
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
        except:
            pass

        return text


# ============ TEXT-TO-SPEECH ============
class TextToSpeech:
    def __init__(self):
        pygame.mixer.init()
        self.temp_files = []

    def synthesize(self, text):
        if not text:
            return None

        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            self.temp_files.append(temp_file.name)

            tts = gTTS(text=text, lang=TARGET_LANGUAGE, slow=False)
            tts.save(temp_file.name)

            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(temp_file.name)
            samples = np.array(audio.get_array_of_samples())

            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1).astype(np.int16)

            return samples.astype(np.int16)

        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    def play_audio(self, audio_array):
        if audio_array is None:
            return

        try:
            audio_bytes = audio_array.tobytes()

            with io.BytesIO() as wav_io:
                import wave
                with wave.open(wav_io, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(SAMPLE_RATE)
                    wav_file.writeframes(audio_bytes)

                wav_io.seek(0)
                sound = pygame.mixer.Sound(wav_io)
                sound.play()

                while pygame.mixer.get_busy():
                    pygame.time.wait(10)
        except Exception as e:
            print(f"Playback error: {e}")

    def __del__(self):
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


# ============ MAIN SYSTEM ============
class SpeechToSpeechSystem:
    def __init__(self):
        print("Initializing Speech-to-Speech System...")
        print("Using FREE APIs (no local models required)\n")

        self.audio_capture = AudioCapture()
        self.noise_suppressor = NoiseSuppression()
        self.vad = VoiceActivityDetector()
        self.lid = LanguageIdentifier()
        self.asr = SpeechRecognizer()
        self.translator = TranslationEngine()
        self.tts = TextToSpeech()

        self.is_running = False
        print("System initialized successfully!\n")

    def process_audio_stream(self):
        print("🎤 Listening... Speak into your microphone\n")
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
                continue

    def process_speech_segment(self, audio_segment):
        print("\n" + "=" * 50)
        print("🎤 Processing speech...")

        try:
            transcribed_text = self.asr.transcribe(audio_segment)

            if not transcribed_text:
                print("No speech detected")
                return

            print(f"📝 Recognized: {transcribed_text}")

            translated_text = self.translator.translate(transcribed_text)
            print(f"🔄 Translation: {translated_text}")

            print(f"🔊 Speaking translation...")
            audio_output = self.tts.synthesize(translated_text)

            if audio_output is not None:
                self.tts.play_audio(audio_output)
                print("✅ Done!")
            else:
                print(f"Text output: {translated_text}")

        except Exception as e:
            print(f"Error: {e}")
        print("=" * 50)

    def start(self):
        print("\n🚀 Starting System...")

        self.is_running = True
        try:
            self.audio_capture.start_capture()
            self.process_audio_stream()
        except KeyboardInterrupt:
            print("\n⏹️  Stopping system...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        try:
            self.audio_capture.stop_capture()
        except:
            pass
        print("✅ System stopped")


if __name__ == "__main__":
    # Install missing package if needed
    try:
        import speech_recognition
    except ImportError:
        print("Installing speech_recognition...")
        os.system("pip install speech_recognition")
        import speech_recognition

    system = SpeechToSpeechSystem()
    system.start()