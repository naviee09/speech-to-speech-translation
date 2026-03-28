import requests
from gtts import gTTS
import pygame
import tempfile
import os

TARGET_LANGUAGE = "en"

def translate(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {'client': 'gtx', 'sl': 'auto', 'tl': TARGET_LANGUAGE, 'dt': 't', 'q': text}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result and result[0]:
            return ''.join([s[0] for s in result[0]])
    return text

def speak(text):
    print(f"\n🔊 Speaking: {text}")
    try:
        temp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp.close()
        tts = gTTS(text=text, lang=TARGET_LANGUAGE)
        tts.save(temp.name)
        pygame.mixer.init()
        pygame.mixer.music.load(temp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.quit()
        os.unlink(temp.name)
    except:
        print(f"Text: {text}")

print("="*50)
print("Text Translation Test")
print("="*50)
print("Enter text to translate (or 'quit' to exit):")

while True:
    text = input("\nEnter text: ")
    if text.lower() == 'quit':
        break
    if text:
        translated = translate(text)
        print(f"Original: {text}")
        print(f"Translated: {translated}")
        speak(translated)
