import speech_recognition as sr
import time

print("="*60)
print("SIMPLE VOICE TO TEXT CONVERTER")
print("="*60)

def list_microphones():
    """List all available microphones"""
    print("\nAvailable microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "Microphone" in name or "Mic" in name or "Input" in name:
            print(f"  {index}: {name}")

def test_microphone():
    """Simple microphone test"""
    print("\nTesting microphone...")
    
    try:
        # Try to get default microphone
        mic = sr.Microphone()
        
        with mic as source:
            print("Adjusting for ambient noise (2 seconds)...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("\n✅ Microphone is ready!")
            print("Speak a few words...")
            
            # Listen for 3 seconds
            print("🎤 Listening... (3 seconds)")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            
            print("✅ Audio captured!")
            
            # Try to recognize
            print("\n🔄 Converting to text...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"\n📝 You said: {text}")
                return True
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return False
            except sr.RequestError as e:
                print(f"❌ Could not request results: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False

def continuous_recording():
    """Record until user stops"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\n" + "="*60)
            print("READY FOR VOICE TO TEXT")
            print("="*60)
            print("Speak clearly into the microphone")
            print("Press Ctrl+C to stop\n")
            
            # Adjust for ambient noise
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ready!\n")
            
            while True:
                print("🎤 Listening... (speak now)")
                
                try:
                    # Listen with timeout
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    print("🔄 Converting to text...")
                    
                    # Recognize
                    text = recognizer.recognize_google(audio)
                    
                    print(f"\n📝 {text}\n")
                    print("-"*60)
                    
                except sr.WaitTimeoutError:
                    print("No speech detected. Waiting...")
                    continue
                except sr.UnknownValueError:
                    print("Could not understand audio. Please speak clearly.")
                    continue
                except sr.RequestError as e:
                    print(f"Network error: {e}")
                    continue
                    
    except KeyboardInterrupt:
        print("\n\nStopping...")

def main():
    print("\n🎤 VOICE TO TEXT CONVERTER")
    print("Using Google Speech Recognition\n")
    
    print("Choose mode:")
    print("1. Test microphone (quick test)")
    print("2. Continuous voice to text")
    print("3. List all microphones")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_microphone()
    elif choice == '2':
        continuous_recording()
    elif choice == '3':
        list_microphones()
        input("\nPress Enter to continue...")
    elif choice == '4':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
