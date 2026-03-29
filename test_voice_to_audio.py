"""
Voice to Audio Test
===================
This is a simple test I wrote to check if voice-to-audio conversion works.
I built this as a prototype before adding translation features.

What this does:
1. Listens to your voice through microphone
2. Converts speech to text using Google's API
3. Converts that text back to speech
4. Plays it through your speakers

I used this to test the core functionality before building the full app.
"""

import speech_recognition as sr
import tempfile
import os
from gtts import gTTS
import pygame

# ============================================
# MAIN TEST FUNCTION
# ============================================

def test_voice_to_audio():
    """
    Test the complete voice-to-audio pipeline
    I wrote this to make sure everything works before adding GUI
    """
    
    print("="*50)
    print("🎤 VOICE TO AUDIO TEST")
    print("="*50)
    print("I built this to test the core functionality")
    print("")
    
    # Initialize speech recognizer
    # I tried different settings here - Google's API works best
    recognizer = sr.Recognizer()
    
    try:
        # Step 1: Capture voice from microphone
        print("📢 STEP 1: Capturing your voice")
        print("   Please speak clearly into your microphone")
        print("")
        
        with sr.Microphone() as source:
            # Adjust for background noise
            # This took me a while to figure out - without this, it was too sensitive
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("🎤 Listening... (you have 5 seconds)")
            print("   Speak now!")
            
            # Listen for speech
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("   ✅ Audio captured!")
            
        # Step 2: Convert voice to text
        print("")
        print("📝 STEP 2: Converting speech to text")
        print("   Sending to Google Speech API...")
        
        text = recognizer.recognize_google(audio)
        print(f"   ✅ You said: \"{text}\"")
        
        # Step 3: Convert text to audio
        print("")
        print("🔊 STEP 3: Converting text back to audio")
        print("   Generating speech...")
        
        # Create temporary file for audio
        # I use temp files to avoid leaving junk on disk
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        # Generate speech using gTTS
        # gTTS gives natural sounding voices - I like it better than offline options
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_file.name)
        print("   ✅ Audio generated!")
        
        # Step 4: Play the audio
        print("")
        print("🔊 STEP 4: Playing audio through speakers")
        print("   Listen carefully...")
        
        # Initialize pygame mixer for playback
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()
        
        print("   🔊 Playing...")
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        print("   ✅ Playback complete!")
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        # Final success message
        print("")
        print("="*50)
        print("✅ TEST COMPLETE!")
        print("="*50)
        print("What just happened:")
        print("   1. Your voice was captured")
        print("   2. Converted to text: \"" + text + "\"")
        print("   3. Text converted back to speech")
        print("   4. Played through your speakers")
        print("")
        print("If you heard your own voice, everything works!")
        
    except sr.WaitTimeoutError:
        print("")
        print("❌ No speech detected!")
        print("   I waited 5 seconds but didn't hear anything")
        print("   Please check:")
        print("   1. Your microphone is plugged in")
        print("   2. Microphone is not muted")
        print("   3. Speak louder next time")
        
    except sr.UnknownValueError:
        print("")
        print("❌ Could not understand audio!")
        print("   Google couldn't understand what you said")
        print("   Try speaking more clearly")
        
    except sr.RequestError as e:
        print("")
        print(f"❌ Network error: {e}")
        print("   Check your internet connection")
        print("   Google API needs internet to work")
        
    except Exception as e:
        print("")
        print(f"❌ Unexpected error: {e}")
        print("   Something went wrong - check your setup")
    
    finally:
        # Clean up pygame
        pygame.mixer.quit()
        print("")
        print("👋 Test complete! Run again to test more")

# ============================================
# RUN THE TEST
# ============================================

if __name__ == "__main__":
    # Check if required libraries are installed
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
    
    if missing:
        print("="*50)
        print("❌ Missing Libraries!")
        print("="*50)
        print("Please install these libraries first:")
        print(f"   pip install {' '.join(missing)}")
        print("")
        print("Then run this test again:")
        print("   python test_voice_to_audio.py")
    else:
        # Run the test
        test_voice_to_audio()
