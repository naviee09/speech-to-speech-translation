"""
COMPLETE SPEECH SYSTEM - WITH VIDEO FEATURES (FIXED)
====================================================
Now I can extract audio from videos too!
Upload any video, get text or speech from it.
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
import time
import base64
from moviepy import VideoFileClip

app = Flask(__name__)

# ============================================
# MY SETTINGS
# ============================================

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 3
SILENCE_LIMIT = 15

# Storage folders
DIARY_FILE = "my_diary.json"
RECORDINGS_FOLDER = "recordings"

if not os.path.exists(RECORDINGS_FOLDER):
    os.makedirs(RECORDINGS_FOLDER)

# ============================================
# DIARY FUNCTIONS
# ============================================

def load_diary():
    try:
        if os.path.exists(DIARY_FILE):
            with open(DIARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_diary(entries):
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
# TEXT TO SPEECH
# ============================================

def text_to_audio(text, lang="en"):
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
# VIDEO FUNCTIONS - FIXED!
# ============================================

@app.route('/video_to_text', methods=['POST'])
def video_to_text():
    """Extract audio from video and convert to text"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file', 'success': False}), 400
        
        video_file = request.files['video']
        video_path = f"{RECORDINGS_FOLDER}/temp_video.mp4"
        video_file.save(video_path)
        
        # Extract audio from video using fixed import
        audio_path = f"{RECORDINGS_FOLDER}/temp_audio.wav"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        # Convert audio to text
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        # Clean up
        os.unlink(video_path)
        os.unlink(audio_path)
        
        return jsonify({'text': text, 'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

@app.route('/video_to_speech', methods=['POST'])
def video_to_speech():
    """Extract audio from video, convert to text, then to speech"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file', 'success': False}), 400
        
        lang = request.form.get('lang', 'en')
        video_file = request.files['video']
        
        video_path = f"{RECORDINGS_FOLDER}/temp_video.mp4"
        video_file.save(video_path)
        
        audio_path = f"{RECORDINGS_FOLDER}/temp_audio.wav"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            original_text = recognizer.recognize_google(audio)
        
        if lang != 'en':
            translated_text = translate_text(original_text, lang)
        else:
            translated_text = original_text
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        speech_file = f"{RECORDINGS_FOLDER}/video_speech_{timestamp}.mp3"
        tts = gTTS(text=translated_text, lang=lang, slow=False)
        tts.save(speech_file)
        
        os.unlink(video_path)
        os.unlink(audio_path)
        
        return jsonify({
            'success': True,
            'original': original_text,
            'translated': translated_text,
            'audio_file': speech_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

@app.route('/video_save_text', methods=['POST'])
def video_save_text():
    """Extract text from video and save as text file"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file', 'success': False}), 400
        
        video_file = request.files['video']
        video_path = f"{RECORDINGS_FOLDER}/temp_video.mp4"
        video_file.save(video_path)
        
        audio_path = f"{RECORDINGS_FOLDER}/temp_audio.wav"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_file = f"{RECORDINGS_FOLDER}/video_text_{timestamp}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"Video Text Extraction\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write(text)
        
        os.unlink(video_path)
        os.unlink(audio_path)
        
        return send_file(text_file, as_attachment=True, download_name=f"video_text_{timestamp}.txt")
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# ROUTES - WEB PAGES
# ============================================

@app.route('/')
def index():
    entries = load_diary()
    return render_template('index.html', entries=entries)

# ============================================
# SPEECH TO TEXT API
# ============================================

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
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
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False})

# ============================================
# TEXT TO SPEECH API
# ============================================

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
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
    data = request.get_json()
    text = data.get('text', '')
    target = data.get('lang', 'en')
    if not text:
        return jsonify({'error': 'No text'}), 400
    translated = translate_text(text, target)
    return jsonify({'original': text, 'translated': translated, 'success': True})

# ============================================
# AUDIO TO TEXT
# ============================================

@app.route('/audio_to_text', methods=['POST'])
def audio_to_text():
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
    entries = load_diary()
    return jsonify({'entries': entries})

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
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
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        lang = request.form.get('lang', 'en')
        audio_file = request.files['audio']
        temp_path = "temp_audio.wav"
        audio_file.save(temp_path)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            original = recognizer.recognize_google(audio)
        
        translated = translate_text(original, lang)
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
    recordings = []
    if os.path.exists(RECORDINGS_FOLDER):
        for file in os.listdir(RECORDINGS_FOLDER):
            if file.endswith(('.wav', '.mp3', '.txt')):
                recordings.append({
                    'name': file,
                    'path': f"/download_recording/{file}",
                    'date': datetime.fromtimestamp(os.path.getmtime(f"{RECORDINGS_FOLDER}/{file}")).strftime("%Y-%m-%d %H:%M:%S")
                })
    return jsonify({'recordings': recordings})

@app.route('/download_recording/<filename>')
def download_recording(filename):
    return send_file(f"{RECORDINGS_FOLDER}/{filename}", as_attachment=True)

# ============================================
# RUN THE APP
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎙️ MY COMPLETE SPEECH SYSTEM WITH VIDEO")
    print("="*60)
    print("Open your browser and go to: http://localhost:5000")
    print("")
    print("What I built:")
    print("   • Speech to Text - Speak, it writes")
    print("   • Text to Speech - Type, it speaks")
    print("   • Audio to Text - Upload audio, get text")
    print("   • Video to Text - Upload video, get text (NEW!)")
    print("   • Video to Speech - Upload video, get speech (NEW!)")
    print("   • Speech Translation - Translate voice")
    print("   • Voice Diary - Save your thoughts")
    print("   • Recordings - Save and download")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
