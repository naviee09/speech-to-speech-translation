"""
Audio Processing Module
=======================
I built this module to handle all audio-related tasks.
This was the hardest part of the project!

What I learned:
- Capturing audio is easy, but making it work reliably is hard
- Different computers have different microphone sensitivities
- Background noise is a real challenge
"""

import pyaudio
import numpy as np
import queue
import webrtcvad
import time

# ============================================
# AUDIO CAPTURE CLASS
# ============================================

class AudioCapture:
    """Handles microphone input and streaming"""
    
    def __init__(self, sample_rate=16000, chunk_size=1024):
        """Initialize the audio capture"""
        
        # Settings - found through trial and error
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Queue for storing audio chunks
        self.audio_queue = queue.Queue()
        
        # Recording state
        self.is_recording = False
        self.stream = None
        self.p = None
        
        # Initialize PyAudio
        self.init_pyaudio()
        
    def init_pyaudio(self):
        """Initialize PyAudio - this took me a while to figure out"""
        try:
            self.p = pyaudio.PyAudio()
            
            # List available microphones (for debugging)
            self.list_microphones()
            
        except Exception as e:
            print(f"Error initializing audio: {e}")
            print("Check if microphone is connected and accessible")
    
    def list_microphones(self):
        """List available microphones - useful for debugging"""
        print("\nAvailable microphones:")
        mic_count = 0
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                mic_count += 1
                print(f"  [{i}] {dev['name']}")
        
        if mic_count == 0:
            print("  No microphones found!")
            print("  Check your microphone connection")
        else:
            print(f"  Found {mic_count} microphone(s)\n")
    
    def start_capture(self):
        """Start capturing audio from microphone"""
        self.is_recording = True
        
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            print("✅ Audio capture started")
            
        except Exception as e:
            print(f"❌ Failed to start capture: {e}")
            self.is_recording = False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream - runs in background"""
        if self.is_recording:
            try:
                audio_data = np.frombuffer(in_data, dtype=np.int16)
                self.audio_queue.put(audio_data)
            except Exception as e:
                print(f"Callback error: {e}")
        
        return (None, pyaudio.paContinue)
    
    def get_audio_chunk(self, timeout=0.05):
        """Get next audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop_capture(self):
        """Stop capturing audio"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.p:
            self.p.terminate()
        
        print("✅ Audio capture stopped")

# ============================================
# NOISE SUPPRESSION CLASS
# ============================================

class NoiseSuppression:
    """Removes background noise from audio"""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.noise_floor = None
        self.alpha = 0.1  # Smoothing factor - I found 0.1 works best
        
        # I tried different values:
        # 0.05: too slow to adapt
        # 0.15: too jumpy
        # 0.10: just right
        
    def spectral_subtraction(self, audio_chunk):
        """Remove noise using spectral subtraction"""
        
        # Convert to frequency domain
        fft = np.fft.rfft(audio_chunk)
        magnitude = np.abs(fft)
        phase = np.angle(fft)
        
        # Update noise floor
        if self.noise_floor is None:
            self.noise_floor = magnitude.copy()
        else:
            self.noise_floor = self.alpha * magnitude + (1 - self.alpha) * self.noise_floor
        
        # Subtract noise
        magnitude_clean = np.maximum(magnitude - self.noise_floor, 0)
        
        # Convert back to time domain
        fft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = np.fft.irfft(fft_clean)
        
        return audio_clean.astype(np.int16)
    
    def process(self, audio_chunk, method='spectral'):
        """Process audio through noise suppression"""
        if method == 'spectral':
            return self.spectral_subtraction(audio_chunk)
        
        # Fallback - return original if method not found
        return audio_chunk

# ============================================
# VOICE ACTIVITY DETECTION CLASS
# ============================================

class VoiceActivityDetector:
    """Detects when someone is speaking"""
    
    def __init__(self, mode=3, sample_rate=16000):
        # VAD mode: 0-3 (0=least aggressive, 3=most aggressive)
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        
        # Frame size - 30ms as recommended by WebRTC
        self.frame_duration_ms = 30
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)
        
        # Speech buffer
        self.speech_buffer = []
        self.silence_counter = 0
        
        # Thresholds - tuned through testing
        self.speech_threshold = 5    # 5 frames = ~0.15s to start
        self.silence_threshold = 15   # 15 frames = ~0.45s silence to stop
        
    def is_speech(self, audio_chunk):
        """Check if audio chunk contains speech"""
        if len(audio_chunk) < self.frame_size:
            return False
        
        # Convert to bytes for VAD
        audio_bytes = audio_chunk.tobytes()
        
        try:
            return self.vad.is_speech(audio_bytes, self.sample_rate)
        except:
            return False
    
    def process_stream(self, audio_chunk):
        """Process streaming audio and return speech segments"""
        
        is_speaking = self.is_speech(audio_chunk)
        
        if is_speaking:
            # Speech detected
            self.silence_counter = 0
            self.speech_buffer.append(audio_chunk)
            
            # Check if we have enough speech frames
            if len(self.speech_buffer) >= self.speech_threshold:
                return self._get_speech_segment()
        
        else:
            # Silence detected
            if len(self.speech_buffer) > 0:
                self.silence_counter += 1
                
                # Check if silence is long enough to end speech
                if self.silence_counter >= self.silence_threshold:
                    return self._get_speech_segment()
        
        return None
    
    def _get_speech_segment(self):
        """Return current speech segment and reset buffer"""
        if self.speech_buffer:
            segment = np.concatenate(self.speech_buffer)
            self.speech_buffer = []
            self.silence_counter = 0
            return segment
        
        return None

# ============================================
# MY NOTES ON AUDIO PROCESSING
# ============================================
# 
# I spent about 2 weeks just on audio processing:
# 
# 1. Week 1: Getting PyAudio to work on Windows
#    - Had to install specific versions
#    - Permissions were tricky
# 
# 2. Week 2: Tuning VAD settings
#    - Too sensitive: kept detecting background noise
#    - Not sensitive enough: missed speech
#    - Found sweet spot with mode=3 and custom thresholds
# 
# 3. Noise Suppression:
#    - Tried 3 different algorithms
#    - Spectral subtraction worked best for me
#    - Still needs improvement in noisy environments
# 
# If I had more time, I'd add:
# - Better noise reduction
# - Echo cancellation
# - Multiple microphone support
# 
