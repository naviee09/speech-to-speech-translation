import pyaudio
import numpy as np
import webrtcvad
import speech_recognition as sr
import tempfile
import wave
import time
import os

print("="*60)
print("ADVANCED VOICE TO TEXT CONVERTER")
print("="*60)

class VoiceToText:
    def __init__(self):
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.vad = webrtcvad.Vad(3)  # Most aggressive
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
    def record_until_silence(self, silence_timeout=1.5, max_duration=10):
        """Record audio until silence is detected"""
        print("\n🎤 Listening... Speak now (will stop after 1.5 seconds of silence)")
        print(f"Maximum recording time: {max_duration} seconds")
        print("Press Ctrl+C to cancel\n")
        
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        speech_frames = []
        silent_frames = 0
        speech_detected = False
        silent_required = int(silence_timeout * 1000 / self.frame_duration_ms)
        
        print("🔊 Speak now...")
        
        # Calculate maximum frames
        max_frames = int(max_duration * 1000 / self.frame_duration_ms)
        frames_recorded = 0
        
        try:
            while frames_recorded < max_frames:
                # Read audio chunk
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                
                # Check for speech
                if len(audio_chunk) >= self.frame_size:
                    is_speech = self.vad.is_speech(audio_chunk.tobytes(), self.sample_rate)
                    
                    if is_speech:
                        if not speech_detected:
                            print("📝 Recording started...")
                            speech_detected = True
                        speech_frames.append(data)
                        silent_frames = 0
                    else:
                        if speech_detected:
                            silent_frames += 1
                            speech_frames.append(data)
                            
                            if silent_frames >= silent_required:
                                print("🔇 Silence detected, stopping recording...")
                                break
                        else:
                            # Still waiting for speech to start
                            pass
                
                frames_recorded += 1
                time.sleep(0.001)
                
            if not speech_detected:
                print("❌ No speech detected")
                return None
                
        except KeyboardInterrupt:
            print("\n⏹️ Recording cancelled")
            return None
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        if not speech_frames:
            return None
            
        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(speech_frames))
        
        print(f"✅ Recorded {len(speech_frames)} frames")
        return temp_file.name
    
    def convert_to_text(self, audio_file):
        """Convert audio to text"""
        print("\n🔄 Converting speech to text...")
        
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.record(source)
                
                # Try multiple recognition methods
                print("🔍 Recognizing...")
                
                # Try Google first
                try:
                    text = recognizer.recognize_google(audio)
                    return text
                except:
                    pass
                
                # Try Sphinx (offline) as fallback
                try:
                    text = recognizer.recognize_sphinx(audio)
                    return text
                except:
                    pass
                    
                return "❌ Could not recognize speech"
                
        except Exception as e:
            return f"❌ Error: {e}"

def test_microphone():
    """Quick microphone test"""
    print("\n" + "="*60)
    print("TESTING MICROPHONE")
    print("="*60)
    
    p = pyaudio.PyAudio()
    
    try:
        # List microphones
        print("\nAvailable microphones:")
        mic_count = 0
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                mic_count += 1
                print(f"  [{i}] {dev['name']}")
        
        if mic_count == 0:
            print("❌ No microphone found!")
            return False
        
        # Test with VAD
        print("\n🎤 Testing microphone... Speak a few words")
        vad = webrtcvad.Vad(3)
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        speech_detected = False
        print("Speak now (testing for 3 seconds)...")
        
        for _ in range(100):  # ~3 seconds
            data = stream.read(1024, exception_on_overflow=False)
            audio = np.frombuffer(data, dtype=np.int16)
            
            if len(audio) >= 480:  # 30ms at 16000Hz
                is_speech = vad.is_speech(audio.tobytes(), 16000)
                if is_speech:
                    speech_detected = True
                    print("✅ Microphone is working!")
                    break
        
        stream.stop_stream()
        stream.close()
        
        if not speech_detected:
            print("⚠️  No speech detected during test")
            print("   Make sure you spoke loudly enough")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False
    finally:
        p.terminate()

def main():
    print("\n🎤 ADVANCED VOICE TO TEXT CONVERTER")
    print("This tool waits for you to finish speaking before converting")
    
    # Test microphone
    if not test_microphone():
        print("\n⚠️  Please check your microphone and try again")
        return
    
    vt = VoiceToText()
    
    while True:
        print("\n" + "="*60)
        print("OPTIONS:")
        print("="*60)
        print("1. Speak and convert to text (waits for you to finish)")
        print("2. Change silence timeout")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Get silence timeout preference
            timeout = 1.5
            custom = input("Use custom silence timeout? (default 1.5s) [y/N]: ").strip().lower()
            if custom == 'y':
                try:
                    timeout = float(input("Enter silence timeout in seconds (0.5-3): "))
                except:
                    print("Using default 1.5 seconds")
            
            # Record and convert
            audio_file = vt.record_until_silence(silence_timeout=timeout)
            
            if audio_file:
                text = vt.convert_to_text(audio_file)
                
                print("\n" + "="*60)
                print("📝 RESULT:")
                print("="*60)
                print(f"Text: {text}")
                print("="*60)
                
                # Clean up
                try:
                    os.unlink(audio_file)
                except:
                    pass
            else:
                print("No audio recorded")
                
        elif choice == '2':
            print("\nSilence timeout controls how long to wait after you stop speaking")
            print("Shorter timeout = faster response, may cut off early")
            print("Longer timeout = more accurate, slower response")
            timeout = float(input("Enter timeout (0.5-3 seconds): "))
            print(f"✅ Silence timeout set to {timeout} seconds")
            
        elif choice == '3':
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
