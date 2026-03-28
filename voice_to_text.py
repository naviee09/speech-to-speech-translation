import pyaudio
import wave
import speech_recognition as sr
import tempfile
import os
import numpy as np

print("="*60)
print("VOICE TO TEXT CONVERTER")
print("="*60)

def record_audio(duration=5):
    """Record audio from microphone"""
    print(f"\n🎤 Recording for {duration} seconds...")
    print("Speak now!")
    
    # Audio settings
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    p = pyaudio.PyAudio()
    
    # Open stream
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    # Record audio
    frames = []
    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    # Stop and close
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save to temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file.close()
    
    with wave.open(temp_file.name, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print("✅ Recording complete!")
    return temp_file.name

def convert_to_text(audio_file):
    """Convert audio file to text using Google Speech Recognition"""
    print("\n🔄 Converting speech to text...")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file) as source:
            # Adjust for ambient noise
            print("📊 Analyzing audio...")
            audio = recognizer.record(source)
            
            # Recognize speech
            print("🔍 Recognizing...")
            text = recognizer.recognize_google(audio)
            return text
            
    except sr.UnknownValueError:
        return "❌ Could not understand audio (speech not clear)"
    except sr.RequestError as e:
        return f"❌ Could not request results: {e}"
    except Exception as e:
        return f"❌ Error: {e}"

def test_microphone():
    """Test if microphone is working"""
    print("\n" + "="*60)
    print("TESTING MICROPHONE")
    print("="*60)
    
    p = pyaudio.PyAudio()
    
    # List available microphones
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
    
    # Test recording
    try:
        print("\n🎤 Testing microphone with a 2-second recording...")
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        # Record short sample
        frames = []
        for _ in range(0, int(16000 / 1024 * 2)):
            data = stream.read(1024)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Check audio level
        audio_data = b''.join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_array))
        
        print(f"📊 Audio level: {max_amplitude}")
        
        if max_amplitude > 500:
            print("✅ Microphone is working!")
            return True
        else:
            print("⚠️  Microphone is detected but audio level is low")
            print("   Check if microphone is properly positioned")
            return False
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False
    finally:
        p.terminate()

def main():
    print("\n🎤 VOICE TO TEXT CONVERTER")
    print("This tool converts your voice to text using Google's speech recognition")
    
    # Test microphone first
    if not test_microphone():
        print("\n⚠️  Please check your microphone and try again")
        print("   Make sure:")
        print("   1. Microphone is plugged in")
        print("   2. Microphone is not muted")
        print("   3. Windows microphone access is enabled (Settings → Privacy → Microphone)")
        return
    
    print("\n" + "="*60)
    print("READY TO CONVERT VOICE TO TEXT")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Record and convert to text (5 seconds)")
        print("2. Record custom duration")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Record for 5 seconds
            audio_file = record_audio(5)
            text = convert_to_text(audio_file)
            
            print("\n" + "="*60)
            print("📝 RESULT:")
            print("="*60)
            print(f"Text: {text}")
            print("="*60)
            
            # Clean up
            os.unlink(audio_file)
            
        elif choice == '2':
            # Custom duration
            try:
                duration = int(input("Enter recording duration (seconds): "))
                if duration > 0:
                    audio_file = record_audio(duration)
                    text = convert_to_text(audio_file)
                    
                    print("\n" + "="*60)
                    print("📝 RESULT:")
                    print("="*60)
                    print(f"Text: {text}")
                    print("="*60)
                    
                    # Clean up
                    os.unlink(audio_file)
            except ValueError:
                print("❌ Invalid duration")
                
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
