import time
from audio.capture import AudioCapture
from audio.noise_suppression import NoiseSuppression
from audio.vad import VoiceActivityDetector
from processing.lid import LanguageIdentifier
from processing.asr import SpeechRecognizer
from processing.translation import TranslationEngine
from processing.tts import TextToSpeech


class SpeechToSpeechSystem:
    def __init__(self):
        print("Initializing Speech-to-Speech System...")
        self.audio_capture = AudioCapture()
        self.noise_suppressor = NoiseSuppression()
        self.vad = VoiceActivityDetector()
        self.lid = LanguageIdentifier()
        self.asr = SpeechRecognizer()
        self.translator = TranslationEngine()
        self.tts = TextToSpeech()

        self.is_running = False
        self.current_language = None
        print("System initialized successfully!")

    def process_audio_stream(self):
        while self.is_running:
            audio_chunk = self.audio_capture.get_audio_chunk(timeout=0.05)

            if audio_chunk is None:
                continue

            audio_clean = self.noise_suppressor.process(audio_chunk)
            speech_segment = self.vad.process_stream(audio_clean)

            if speech_segment is not None:
                self.process_speech_segment(speech_segment)

    def process_speech_segment(self, audio_segment):
        print("\n🎤 Processing speech segment...")

        transcribed_text = self.asr.transcribe(audio_segment)

        if not transcribed_text:
            print("No speech detected")
            return

        print(f"📝 Transcribed: {transcribed_text}")

        if self.current_language is None:
            detected_lang, confidence = self.lid.identify(transcribed_text)
            self.current_language = detected_lang
            print(f"🌐 Language detected: {detected_lang} (confidence: {confidence:.2f})")

        translated_text = self.translator.translate(transcribed_text)
        print(f"🔄 Translated: {translated_text}")

        audio_output = self.tts.synthesize(translated_text)

        if audio_output is not None:
            print(f"🔊 Playing synthesized speech...")
            self.tts.play_audio(audio_output)

    def start(self):
        print("\n🚀 Starting Speech-to-Speech Translation System...")
        print("🎙️  Speak into your microphone...")
        print("Press Ctrl+C to stop\n")

        self.is_running = True
        self.audio_capture.start_capture()

        try:
            self.process_audio_stream()
        except KeyboardInterrupt:
            print("\n⏹️  Stopping system...")
        finally:
            self.stop()

    def stop(self):
        self.is_running = False
        self.audio_capture.stop_capture()
        print("✅ System stopped")


if __name__ == "__main__":
    system = SpeechToSpeechSystem()
    system.start()