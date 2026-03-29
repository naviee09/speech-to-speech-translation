"""
COMPLETE SPEECH SYSTEM - WEB VERSION
=====================================
I built this to run in my browser on localhost.
Everything works with voice - text to speech, speech to text, recording, translation, diary.

This is my complete project that I built over 4 weeks.
"""

from flask import Flask, render_template, request, jsonify, send_file
import speech_recognition as sr
import tempfile
import os
import wave
import pyaudio
import webrtcvad
import numpy as np
from datetime import datetime
import json
import requests
from gtts import gTTS
import pygame
import threading
import time
import base64

app = Flask(__name__)

# ============================================
# MY SETTINGS - FOUND THROUGH TESTING
# ============================================

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3
SILENCE_LIMIT = 15

# My diary storage
DIARY_FILE = "my_diary.json"
RECORDINGS_FOLDER = "recordings"

# Create recordings folder if it doesn't exist
if not os.path.exists(RECORDINGS_FOLDER):
    os.makedirs(RECORDINGS_FOLDER)

# ============================================
# DIARY FUNCTIONS
# ============================================

def load_diary():
    """Load my saved diary entries"""
    try:
        if os.path.exists(DIARY_FILE):
            with open(DIARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_diary(entries):
    """Save my diary entries"""
    try:
        with open(DIARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

# ============================================
# TRANSLATION FUNCTION
# ============================================

def translate_text(text, target_lang="en"):
    """Translate text using Google's free API"""
    if not text:
        return text
    
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0]:
                return ''.join([s[0] for s in data[0]])
    except:
        pass
    
    return text

# ============================================
# TEXT TO SPEECH (SAVE AS AUDIO)
# ============================================

def text_to_audio(text, lang="en"):
    """Convert text to speech and save as audio file"""
    if not text:
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RECORDINGS_FOLDER}/speech_{timestamp}.mp3"
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        
        return filename
    except Exception as e:
        print(f"TTS error: {e}")
        return None

# ============================================
# ROUTES - WEB PAGES
# ============================================

@app.route('/')
def index():
    """Main page - my speech system"""
    entries = load_diary()
    return render_template('index.html', entries=entries)

# ============================================
# SPEECH TO TEXT API
# ============================================

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    """Convert speech to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file', 'success': False}), 400
        
        audio_file = request.files['audio']
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        os.unlink(temp_path)
        
        return jsonify({'text': text, 'success': True})
        
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand', 'success': False})
    except sr.RequestError:
        return jsonify({'error': 'Network error', 'success': False})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# TEXT TO SPEECH API
# ============================================

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'No text'}), 400
    
    audio_file = text_to_audio(text, lang)
    
    if audio_file:
        return send_file(audio_file, mimetype='audio/mpeg', as_attachment=True, download_name='speech.mp3')
    
    return jsonify({'error': 'Failed'}), 500

# ============================================
# TRANSLATION API
# ============================================

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text"""
    data = request.get_json()
    text = data.get('text', '')
    target = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'No text'}), 400
    
    translated = translate_text(text, target)
    return jsonify({'original': text, 'translated': translated, 'success': True})

# ============================================
# AUDIO TO TEXT (UPLOAD FILE)
# ============================================

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text():
    """Convert uploaded audio file to text"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file', 'success': False}), 400
        
        audio_file = request.files['audio']
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        os.unlink(temp_path)
        
        return jsonify({'text': text, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# SAVE RECORDING
# ============================================

@app.route('/save_recording', methods=['POST'])
def save_recording():
    """Save recorded audio to file"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        audio_file = request.files['audio']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RECORDINGS_FOLDER}/recording_{timestamp}.wav"
        audio_file.save(filename)
        
        return jsonify({'filename': filename, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# DIARY API
# ============================================

@app.route('/add_entry', methods=['POST'])
def add_entry():
    """Add diary entry"""
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    
    if not title:
        return jsonify({'error': 'Title required'}), 400
    
    entries = load_diary()
    
    now = datetime.now()
    entry = {
        "id": len(entries) + 1,
        "title": title,
        "content": content,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    entries.append(entry)
    save_diary(entries)
    
    return jsonify({'success': True, 'entry': entry})

@app.route('/get_entries', methods=['GET'])
def get_entries():
    """Get all diary entries"""
    entries = load_diary()
    return jsonify({'entries': entries})

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete diary entry"""
    entries = load_diary()
    
    for i, entry in enumerate(entries):
        if entry['id'] == entry_id:
            del entries[i]
            save_diary(entries)
            return jsonify({'success': True})
    
    return jsonify({'error': 'Not found'}), 404

# ============================================
# SPEECH TO SPEECH TRANSLATION
# ============================================

@app.route('/speech_to_speech', methods=['POST'])
def speech_to_speech():
    """Record speech, translate, and play back"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        lang = request.form.get('lang', 'en')
        audio_file = request.files['audio']
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        # Speech to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            original = recognizer.recognize_google(audio)
        
        # Translate
        translated = translate_text(original, lang)
        
        # Text to speech
        audio_output = text_to_audio(translated, lang)
        
        os.unlink(temp_path)
        
        return jsonify({
            'success': True,
            'original': original,
            'translated': translated,
            'audio': audio_output
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# LIST RECORDINGS
# ============================================

@app.route('/get_recordings', methods=['GET'])
def get_recordings():
    """List all saved recordings"""
    recordings = []
    if os.path.exists(RECORDINGS_FOLDER):
        for file in os.listdir(RECORDINGS_FOLDER):
            if file.endswith(('.wav', '.mp3')):
                recordings.append({
                    'name': file,
                    'path': f"/download_recording/{file}",
                    'date': datetime.fromtimestamp(os.path.getmtime(f"{RECORDINGS_FOLDER}/{file}")).strftime("%Y-%m-%d %H:%M:%S")
                })
    return jsonify({'recordings': recordings})

@app.route('/download_recording/<filename>')
def download_recording(filename):
    """Download a recording"""
    return send_file(f"{RECORDINGS_FOLDER}/{filename}", as_attachment=True)

# ============================================
# RUN THE APP
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎙️ MY COMPLETE SPEECH SYSTEM")
    print("="*60)
    print("Open your browser and go to: http://localhost:5000")
    print("")
    print("What I built:")
    print("   • Speech to Text - Speak, it writes")
    print("   • Text to Speech - Type, it speaks")
    print("   • Audio to Text - Upload audio, get text")
    print("   • Text to Audio - Save text as audio")
    print("   • Speech to Speech - Translate voice")
    print("   • Voice Diary - Save your thoughts")
    print("   • Recordings - Save and download")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
