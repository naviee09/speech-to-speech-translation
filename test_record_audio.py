"""
Voice Recording with Audio Output
=================================
This test does 3 things:
1. Records what you speak and saves it as a WAV file
2. Converts your speech to text
3. Saves the translated/recognized speech as an MP3 file

I built this to save my voice recordings for later use.
"""

import speech_recognition as sr
import tempfile
import os
from gtts import gTTS
import pygame
import wave
import pyaudio
import numpy as np
from datetime import datetime

# ============================================
# AUDIO SETTINGS
# ============================================

# Settings I found work best
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1
AUDIO_FORMAT = pyaudio.paInt16

# ============================================
# FUNCTION TO RECORD AND SAVE AUDIO
# ============================================

def record_and_save_audio(duration=5, filename=None):
    """
    Record audio from microphone and save as WAV file
    I added this to save my voice recordings
    """
    
    print(f"\n🎤 Recording for {duration} seconds...")
    print("   Speak clearly into your microphone")
    
    # Create filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Open stream
    stream = p.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    # Record audio
    frames = []
    print("   🔴 Recording...")
    
    for i in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(data)
    
    print("   ⏹️ Recording stopped")
    
    # Stop and close stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save to WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(AUDIO_FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"   ✅ Audio saved to: {filename}")
    
    return filename, frames

# ============================================
# FUNCTION TO CONVERT VOICE TO TEXT
# ============================================

def voice_to_text(duration=5):
    """
    Listen to voice and convert to text
    This uses Google's Speech Recognition API
    """
    
    print(f"\n🎤 Listening for {duration} seconds...")
    print("   Speak clearly into your microphone")
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("   🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("   🎧 Listening...")
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            print("   🔄 Converting to text...")
            text = recognizer.recognize_google(audio)
            
            print(f"   ✅ You said: \"{text}\"")
            return text
            
    except sr.WaitTimeoutError:
        print("   ❌ No speech detected!")
        return None
    except sr.UnknownValueError:
        print("   ❌ Could not understand audio!")
        return None
    except sr.RequestError as e:
        print(f"   ❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# ============================================
# FUNCTION TO SAVE TEXT AS AUDIO
# ============================================

def save_text_as_audio(text, filename=None, language="en"):
    """
    Convert text to speech and save as MP3 file
    This creates an audio file of what was recognized
    """
    
    if not text:
        print("   ❌ No text to convert")
        return None
    
    # Create filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"speech_output_{timestamp}.mp3"
    
    print(f"\n🔊 Converting text to speech...")
    print(f"   Text: \"{text}\"")
    
    try:
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)
        
        print(f"   ✅ Audio saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

# ============================================
# FUNCTION TO PLAY AUDIO FILE
# ============================================

def play_audio_file(filename):
    """
    Play an audio file
    """
    
    if not filename or not os.path.exists(filename):
        print(f"   ❌ File not found: {filename}")
        return False
    
    try:
        print(f"\n🔊 Playing audio: {filename}")
        
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        print("   🔊 Playing...")
        
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        pygame.mixer.quit()
        print("   ✅ Playback complete")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

# ============================================
# MAIN TEST FUNCTION
# ============================================

def test_voice_recording():
    """
    Complete test: Record voice → Save as WAV → Convert to text → Save as MP3 → Play
    """
    
    print("="*60)
    print("🎙️ VOICE RECORDING & AUDIO OUTPUT TEST")
    print("="*60)
    print("This test will:")
    print("   1. Record your voice and save as WAV")
    print("   2. Convert your speech to text")
    print("   3. Save the recognized text as MP3")
    print("   4. Play both recordings back")
    print("="*60)
    
    # Step 1: Ask for recording duration
    print("\n" + "="*60)
    print("STEP 1: Choose Recording Settings")
    print("="*60)
    
    try:
        duration = int(input("\nHow many seconds to record? (3-10 seconds): ") or 5)
        duration = max(3, min(10, duration))
    except:
        duration = 5
    
    print(f"\n✅ Recording duration: {duration} seconds")
    
    # Step 2: Record voice and save as WAV
    print("\n" + "="*60)
    print("STEP 2: Recording Your Voice")
    print("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_filename = f"my_voice_{timestamp}.wav"
    
    recorded_file, frames = record_and_save_audio(duration, wav_filename)
    
    # Step 3: Convert voice to text
    print("\n" + "="*60)
    print("STEP 3: Converting Voice to Text")
    print("="*60)
    
    text = voice_to_text(duration)
    
    if text:
        # Step 4: Save text as audio
        print("\n" + "="*60)
        print("STEP 4: Saving Text as Audio")
        print("="*60)
        
        mp3_filename = f"text_to_speech_{timestamp}.mp3"
        audio_file = save_text_as_audio(text, mp3_filename)
        
        # Step 5: Play both recordings
        print("\n" + "="*60)
        print("STEP 5: Playing Your Recordings")
        print("="*60)
        
        print("\n🎵 Playing your original voice recording...")
        play_audio_file(recorded_file)
        
        print("\n🎵 Playing the text-to-speech version...")
        play_audio_file(audio_file)
        
        # Summary
        print("\n" + "="*60)
        print("✅ TEST COMPLETE!")
        print("="*60)
        print("\nFiles saved:")
        print(f"   📁 Original voice: {recorded_file}")
        print(f"   📁 Text-to-speech: {audio_file}")
        print(f"\nRecognized text: \"{text}\"")
        print("\nYou can find these files in your project folder!")
        
    else:
        print("\n" + "="*60)
        print("❌ TEST FAILED - No speech detected")
        print("="*60)
        print("\nTroubleshooting:")
        print("   1. Make sure microphone is plugged in")
        print("   2. Check Windows Settings → Privacy → Microphone")
        print("   3. Speak louder and clearer")
        print("   4. Try again with longer duration")

# ============================================
# QUICK RECORD FUNCTION
# ============================================

def quick_record():
    """
    Quick record without translation - just save your voice
    """
    
    print("="*60)
    print("🎤 QUICK VOICE RECORDER")
    print("="*60)
    
    try:
        duration = int(input("\nRecord for how many seconds? (3-10): ") or 5)
        duration = max(3, min(10, duration))
    except:
        duration = 5
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"my_voice_{timestamp}.wav"
    
    record_and_save_audio(duration, filename)
    
    print(f"\n✅ Voice saved to: {filename}")
    print("\nWant to play it back?")
    play = input("Play now? (y/n): ").lower()
    
    if play == 'y':
        play_audio_file(filename)

# ============================================
# MENU SYSTEM
# ============================================

def main_menu():
    """
    Main menu for choosing what to do
    """
    
    while True:
        print("\n" + "="*60)
        print("🎙️ VOICE RECORDING & AUDIO SYSTEM")
        print("="*60)
        print("1. Complete Test (Record → Text → Audio → Play)")
        print("2. Quick Record (Just save your voice)")
        print("3. Play Audio File")
        print("4. Exit")
        print("="*60)
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            test_voice_recording()
        elif choice == '2':
            quick_record()
        elif choice == '3':
            filename = input("Enter audio filename: ").strip()
            if filename:
                play_audio_file(filename)
            else:
                print("No filename provided")
        elif choice == '4':
            print("\n👋 Goodbye! Your recordings are saved in the project folder")
            break
        else:
            print("Invalid choice, please try again")

# ============================================
# RUN THE PROGRAM
# ============================================

if __name__ == "__main__":
    # Check for required libraries
    missing = []
    
    try:
        import speech_recognition
    except:
        missing.append("SpeechRecognition")
    
    try:
        import gtts
    except:
        missing.append("gTTS")
    
    try:
        import pygame
    except:
        missing.append("pygame")
    
    try:
        import pyaudio
    except:
        missing.append("pyaudio")
    
    if missing:
        print("="*60)
        print("❌ Missing Libraries!")
        print("="*60)
        print("Please install:")
        print(f"   pip install {' '.join(missing)}")
        print("\nThen run again:")
        print("   python test_record_audio.py")
    else:
        main_menu()
