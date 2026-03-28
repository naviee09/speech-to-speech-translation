import numpy as np
import pygame
import tempfile
from config import Config


class TextToSpeech:
    def __init__(self, use_api=False):
        self.use_api = use_api
        self.sample_rate = Config.SAMPLE_RATE
        self.model = None
        pygame.mixer.init()

        if not use_api:
            try:
                self._load_model()
            except:
                self.use_api = True

    def _load_model(self):
        from TTS.api import TTS
        self.model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

    def synthesize_local(self, text):
        if not self.model:
            return None

        output_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
        self.model.tts_to_file(text=text, file_path=output_path)

        import soundfile as sf
        audio, sr = sf.read(output_path)

        if sr != self.sample_rate:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)

        return (audio * 32767).astype(np.int16)

    def synthesize(self, text):
        if not text:
            return None

        if self.use_api:
            return None
        else:
            return self.synthesize_local(text)

    def play_audio(self, audio_array):
        if audio_array is None:
            return

        audio_bytes = audio_array.tobytes()

        import io
        import wave

        with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)

            wav_io.seek(0)
            sound = pygame.mixer.Sound(wav_io)
            sound.play()

            while pygame.mixer.get_busy():
                pygame.time.wait(10)