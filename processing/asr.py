import whisper
import numpy as np
from config import Config


class SpeechRecognizer:
    def __init__(self, model_name=Config.ASR_MODEL, use_api=False):
        self.use_api = use_api
        self.model_name = model_name
        self.model = None
        self.sample_rate = Config.SAMPLE_RATE

        if not use_api:
            try:
                self._load_model()
            except:
                self.use_api = True

    def _load_model(self):
        self.model = whisper.load_model(self.model_name)

    def transcribe_local(self, audio_array):
        if not self.model:
            return ""

        audio_float = audio_array.astype(np.float32) / 32768.0
        result = self.model.transcribe(audio_float, language=Config.ASR_LANGUAGE)
        return result["text"]

    def transcribe(self, audio_array):
        if len(audio_array) < self.sample_rate * 0.5:
            return ""

        if self.use_api:
            return ""
        else:
            return self.transcribe_local(audio_array)