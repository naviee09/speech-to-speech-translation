import numpy as np


class NoiseSuppression:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.noise_floor = None
        self.alpha = 0.1

    def spectral_subtraction(self, audio_chunk):
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

    def process(self, audio_chunk, method='spectral'):
        if method == 'spectral':
            return self.spectral_subtraction(audio_chunk)
        return audio_chunk