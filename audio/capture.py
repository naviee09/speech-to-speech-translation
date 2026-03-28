import pyaudio
import numpy as np
import queue
from config import Config


class AudioCapture:
    def __init__(self, sample_rate=Config.SAMPLE_RATE, chunk_size=Config.CHUNK_SIZE):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None
        self.p = pyaudio.PyAudio()

    def start_capture(self):
        self.is_recording = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=Config.CHANNELS,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
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