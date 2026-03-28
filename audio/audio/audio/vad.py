import webrtcvad
import numpy as np
from config import Config


class VoiceActivityDetector:
    def __init__(self, mode=Config.VAD_MODE, sample_rate=Config.SAMPLE_RATE):
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        self.frame_duration_ms = Config.VAD_FRAME_MS
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        self.speech_buffer = []
        self.silence_counter = 0
        self.speech_threshold = 5
        self.silence_threshold = 15

    def is_speech(self, audio_chunk):
        if len(audio_chunk) < self.frame_size:
            return False

        audio_bytes = audio_chunk.tobytes()

        try:
            return self.vad.is_speech(audio_bytes, self.sample_rate)
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