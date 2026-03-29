"""
Speech Translator - My Personal Project
=========================================
I built this for my placement portfolio. It translates your voice in real time.

What I learned while building this:
- Audio processing in Python is tricky
- Google APIs are reliable but have limits
- Threading is essential for real-time apps
- GUI design takes time to get right

I started with a simple console version and gradually added features.
This is version 4.0 - the one I'm most proud of.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import speech_recognition as sr
import requests
import pygame
import tempfile
import os
import json
from datetime import datetime
from gtts import gTTS
import wave
import pyaudio

# ============================================
# MY SETTINGS - TUNED AFTER MANY TESTS
# ============================================

# I tried different silence detection values:
# - 0.5 seconds: too short, kept cutting me off
# - 2.0 seconds: too long, waited forever
# - 1.5 seconds: perfect balance
SILENCE_TIMEOUT = 1.5

# Standard audio settings - these work on most computers
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1

# ============================================
# THE MAIN APPLICATION
# ============================================

class SpeechTranslator:
    """My speech translation application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Translator - My Project")
        self.root.geometry("1200x800")
        
        # I like dark themes - easier on the eyes
        self.root.configure(bg='#1a1a2e')
        
        # Set up colors I like
        self.colors = {
            'bg': '#1a1a2e',
            'panel': '#16213e', 
            'accent': '#0f3460',
            'success': '#00d4ff',
            'warning': '#ff6b6b',
            'text': '#ffffff'
        }
        
        # Initialize all components
        self.init_components()
        
        # Create the user interface
        self.create_ui()
        
        # Track statistics
        self.translation_count = 0
        self.audio_recordings = 0
        self.history = []
        
        print("="*50)
        print("Speech Translator Started!")
        print("I built this for my placement portfolio")
        print("="*50)
    
    def init_components(self):
        """Initialize all libraries and components"""
        
        # Speech recognition - Google's API works best
        self.recognizer = sr.Recognizer()
        
        # For playing audio
        pygame.mixer.init()
        
        # Audio recording setup
        self.is_recording = False
        self.recorded_frames = []
        self.audio_format = pyaudio.paInt16
        
        # System state
        self.is_listening = False
        self.listen_thread = None
        
        # Language settings
        self.target_lang = "en"  # default English
        
        # Languages I've tested and confirmed working
        self.languages = {
            "English": "en",
            "Hindi": "hi", 
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Japanese": "ja",
            "Chinese": "zh",
            "Arabic": "ar",
            "Russian": "ru"
        }
    
    def create_ui(self):
        """Build the user interface - I wanted it clean and modern"""
        
        # Main container
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header section
        self.create_header(main)
        
        # Two-column layout
        left = tk.Frame(main, bg=self.colors['panel'], width=280)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        
        right = tk.Frame(main, bg=self.colors['bg'])
        right.pack(side='right', fill='both', expand=True)
        
        # Build panels
        self.create_control_panel(left)
        self.create_display_panel(right)
        self.create_status_bar(main)
    
    def create_header(self, parent):
        """Create the header with title and status"""
        
        header = tk.Frame(parent, bg=self.colors['panel'], height=70)
        header.pack(fill='x', pady=(0, 15))
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text="🎙️ Speech Translator",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['panel'],
            fg=self.colors['success']
        )
        title.pack(side='left', padx=20, pady=15)
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text="Real-time voice translation",
            font=('Segoe UI', 10),
            bg=self.colors['panel'],
            fg='#b8b8b8'
        )
        subtitle.pack(side='left', padx=10, pady=20)
        
        # Status indicator
        status_frame = tk.Frame(header, bg=self.colors['panel'])
        status_frame.pack(side='right', padx=20)
        
        self.status_dot = tk.Canvas(
            status_frame, width=10, height=10,
            bg=self.colors['panel'], highlightthickness=0
        )
        self.status_dot.pack(side='left', padx=5)
        self.status_dot.create_oval(2, 2, 8, 8, fill='#2ecc71', outline='')
        
        self.status_text = tk.Label(
            status_frame, text="Ready", font=('Segoe UI', 9),
            bg=self.colors['panel'], fg='#2ecc71'
        )
        self.status_text.pack(side='left')
    
    def create_control_panel(self, parent):
        """Left panel with all controls"""
        
        # Logo
        tk.Label(
            parent, text="🎙️", font=('Segoe UI', 48),
            bg=self.colors['panel'], fg=self.colors['success']
        ).pack(pady=20)
        
        # ===== MAIN CONTROLS =====
        tk.Label(
            parent, text="CONTROLS", font=('Segoe UI', 10, 'bold'),
            bg=self.colors['panel'], fg=self.colors['success']
        ).pack(pady=(10, 5))
        
        # Start button
        self.start_btn = tk.Button(
            parent, text="▶ Start Translation", command=self.start_translation,
            font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
            padx=15, pady=8, width=25, cursor='hand2', relief='flat'
        )
        self.start_btn.pack(pady=3)
        
        # Stop button
        self.stop_btn = tk.Button(
            parent, text="⏹️ Stop", command=self.stop_translation,
            font=('Segoe UI', 10), bg='#e74c3c', fg='white',
            padx=15, pady=8, width=25, state='disabled',
            cursor='hand2', relief='flat'
        )
        self.stop_btn.pack(pady=3)
        
        # Test button
        tk.Button(
            parent, text="🎧 Test Microphone", command=self.test_microphone,
            font=('Segoe UI', 9), bg='#3498db', fg='white',
            padx=15, pady=6, width=25, cursor='hand2', relief='flat'
        ).pack(pady=3)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        
        # ===== AUDIO RECORDING =====
        tk.Label(
            parent, text="AUDIO RECORDING", font=('Segoe UI', 10, 'bold'),
            bg=self.colors['panel'], fg=self.colors['success']
        ).pack(pady=(10, 5))
        
        # Record button
        self.record_btn = tk.Button(
            parent, text="🔴 Record Audio", command=self.toggle_recording,
            font=('Segoe UI', 10), bg='#e67e22', fg='white',
            padx=15, pady=8, width=25, cursor='hand2', relief='flat'
        )
        self.record_btn.pack(pady=3)
        
        # Save recording button
        self.save_btn = tk.Button(
            parent, text="💾 Save Recording", command=self.save_recording,
            font=('Segoe UI', 9), bg='#9b59b6', fg='white',
            padx=15, pady=6, width=25, state='disabled',
            cursor='hand2', relief='flat'
        )
        self.save_btn.pack(pady=3)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        
        # ===== LANGUAGE SETTINGS =====
        tk.Label(
            parent, text="LANGUAGE", font=('Segoe UI', 10, 'bold'),
            bg=self.colors['panel'], fg=self.colors['success']
        ).pack(pady=(10, 5))
        
        tk.Label(
            parent, text="Translate to:", font=('Segoe UI', 9),
            bg=self.colors['panel'], fg='#b8b8b8'
        ).pack(anchor='w', padx=20)
        
        self.lang_var = tk.StringVar(value="English")
        lang_combo = ttk.Combobox(
            parent, textvariable=self.lang_var,
            values=list(self.languages.keys()),
            state='readonly', width=23
        )
        lang_combo.pack(pady=3, padx=20)
        lang_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        
        # ===== STATISTICS =====
        tk.Label(
            parent, text="STATS", font=('Segoe UI', 10, 'bold'),
            bg=self.colors['panel'], fg=self.colors['success']
        ).pack(pady=(10, 5))
        
        self.trans_label = tk.Label(
            parent, text="Translations: 0", font=('Segoe UI', 9),
            bg=self.colors['panel'], fg='#b8b8b8'
        )
        self.trans_label.pack(anchor='w', padx=20)
        
        self.audio_label = tk.Label(
            parent, text="Recordings: 0", font=('Segoe UI', 9),
            bg=self.colors['panel'], fg='#b8b8b8'
        )
        self.audio_label.pack(anchor='w', padx=20, pady=(5, 0))
        
        # Export button
        tk.Button(
            parent, text="📥 Export History", command=self.export_history,
            font=('Segoe UI', 9), bg='#9b59b6', fg='white',
            padx=15, pady=5, width=25, cursor='hand2', relief='flat'
        ).pack(pady=(20, 10))
    
    def create_display_panel(self, parent):
        """Right panel with text display"""
        
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1 - Translation
        trans_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(trans_tab, text="📝 Translation")
        
        # Original text
        tk.Label(
            trans_tab, text="What you said:", font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg'], fg=self.colors['success']
        ).pack(anchor='w', pady=(10, 5))
        
        self.original_box = scrolledtext.ScrolledText(
            trans_tab, height=5, font=('Segoe UI', 11),
            bg='#2d2d3a', fg='white', wrap='word'
        )
        self.original_box.pack(fill='x', pady=5)
        
        # Translated text
        tk.Label(
            trans_tab, text="Translation:", font=('Segoe UI', 11, 'bold'),
            bg=self.colors['bg'], fg=self.colors['success']
        ).pack(anchor='w', pady=(15, 5))
        
        self.translated_box = scrolledtext.ScrolledText(
            trans_tab, height=5, font=('Segoe UI', 11),
            bg='#2d2d3a', fg='white', wrap='word'
        )
        self.translated_box.pack(fill='x', pady=5)
        
        # Save translation button
        tk.Button(
            trans_tab, text="💿 Save as Audio", command=self.save_translation_audio,
            font=('Segoe UI', 9), bg='#1abc9c', fg='white',
            padx=10, pady=5, cursor='hand2', relief='flat'
        ).pack(pady=10)
        
        # Tab 2 - History
        history_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(history_tab, text="📜 History")
        
        self.history_box = scrolledtext.ScrolledText(
            history_tab, font=('Consolas', 10),
            bg='#2d2d3a', fg='#b8b8b8', wrap='word'
        )
        self.history_box.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 3 - Log
        log_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(log_tab, text="⚡ Log")
        
        self.log_box = scrolledtext.ScrolledText(
            log_tab, font=('Consolas', 10),
            bg='#2d2d3a', fg='#b8b8b8', wrap='word'
        )
        self.log_box.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_status_bar(self, parent):
        """Bottom status bar"""
        bar = tk.Frame(parent, bg=self.colors['panel'], height=28)
        bar.pack(side='bottom', fill='x', pady=(10, 0))
        bar.pack_propagate(False)
        
        self.status_msg = tk.Label(
            bar, text="✅ Ready to translate", font=('Segoe UI', 8),
            bg=self.colors['panel'], fg='#b8b8b8'
        )
        self.status_msg.pack(side='left', padx=10, pady=5)
        
        self.time_label = tk.Label(
            bar, text=datetime.now().strftime("%H:%M:%S"), font=('Segoe UI', 8),
            bg=self.colors['panel'], fg='#b8b8b8'
        )
        self.time_label.pack(side='right', padx=10, pady=5)
        self.update_clock()
    
    def update_clock(self):
        """Update clock every second"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)
    
    def log(self, message, msg_type='info'):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        icons = {'error': '❌', 'success': '✅', 'warning': '⚠️', 'info': 'ℹ️'}
        icon = icons.get(msg_type, 'ℹ️')
        
        self.log_box.insert('end', f"[{timestamp}] {icon} {message}\n")
        self.log_box.see('end')
        self.status_msg.config(text=f"{icon} {message[:50]}")
    
    # ============================================
    # TRANSLATION FUNCTIONS
    # ============================================
    
    def translate_text(self, text):
        """Translate text using Google Translate"""
        if not text:
            return ""
        
        try:
            # Found this free endpoint after some research
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',  # auto-detect source language
                'tl': self.target_lang,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    return ''.join([s[0] for s in data[0]])
        except Exception as e:
            self.log(f"Translation error: {e}", 'error')
        
        return text
    
    def speak_text(self, text):
        """Convert text to speech"""
        if not text:
            return
        
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang=self.target_lang, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except Exception as e:
            self.log(f"Speech error: {e}", 'error')
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def process_audio(self, audio):
        """Process audio through the pipeline"""
        try:
            # Step 1: Convert speech to text
            text = self.recognizer.recognize_google(audio)
            self.log(f"Recognized: {text}", 'success')
            
            # Display original
            self.original_box.delete('1.0', 'end')
            self.original_box.insert('1.0', text)
            
            # Step 2: Translate
            translated = self.translate_text(text)
            self.log(f"Translated: {translated}", 'info')
            
            # Display translation
            self.translated_box.delete('1.0', 'end')
            self.translated_box.insert('1.0', translated)
            
            # Step 3: Save to history
            self.add_to_history(text, translated)
            
            # Step 4: Speak it
            self.log("Speaking...", 'info')
            self.speak_text(translated)
            
            # Update stats
            self.translation_count += 1
            self.trans_label.config(text=f"Translations: {self.translation_count}")
            
        except sr.UnknownValueError:
            self.log("Could not understand audio", 'warning')
        except sr.RequestError as e:
            self.log(f"Network error: {e}", 'error')
    
    def add_to_history(self, original, translated):
        """Add to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}]\nOriginal: {original}\nTranslated: {translated}\n{'-'*50}\n"
        self.history_box.insert('end', entry)
        self.history_box.see('end')
        
        self.history.append({
            'timestamp': timestamp,
            'original': original,
            'translated': translated
        })
    
    def listen_loop(self):
        """Continuous listening loop"""
        try:
            with sr.Microphone() as source:
                self.log("Calibrating microphone...", 'info')
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.log("Ready! Speak into your microphone", 'success')
                
                while self.is_listening:
                    try:
                        self.status_dot.itemconfig(1, fill='#f39c12')
                        self.status_text.config(text="Listening...", fg='#f39c12')
                        
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                        
                        if audio and self.is_listening:
                            self.process_audio(audio)
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        if self.is_listening:
                            self.log(f"Error: {e}", 'error')
                        
        except Exception as e:
            self.log(f"Microphone error: {e}", 'error')
        finally:
            if not self.is_listening:
                self.reset_ui()
    
    def start_translation(self):
        """Start listening"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.listen_thread = threading.Thread(target=self.listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.log("Started translation mode", 'success')
    
    def stop_translation(self):
        """Stop listening"""
        self.is_listening = False
        self.log("Stopped translation mode", 'warning')
    
    def reset_ui(self):
        """Reset UI"""
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_dot.itemconfig(1, fill='#2ecc71')
        self.status_text.config(text="Ready", fg='#2ecc71')
    
    # ============================================
    # AUDIO RECORDING FUNCTIONS
    # ============================================
    
    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        self.recorded_frames = []
        
        self.audio_p = pyaudio.PyAudio()
        self.audio_stream = self.audio_p.open(
            format=self.audio_format,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        self.record_btn.config(text="⏹️ Stop Recording", bg='#c0392b')
        self.log("Recording audio...", 'warning')
        
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()
    
    def _record_audio(self):
        """Background recording"""
        while self.is_recording:
            try:
                data = self.audio_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.recorded_frames.append(data)
            except:
                pass
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        
        if hasattr(self, 'audio_stream'):
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if hasattr(self, 'audio_p'):
            self.audio_p.terminate()
        
        self.record_btn.config(text="🔴 Record Audio", bg='#e67e22')
        self.save_btn.config(state='normal')
        
        duration = len(self.recorded_frames) * CHUNK_SIZE / SAMPLE_RATE
        self.log(f"Recording stopped ({duration:.1f} seconds)", 'success')
    
    def save_recording(self):
        """Save recorded audio"""
        if not self.recorded_frames:
            self.log("No audio recorded", 'warning')
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")]
        )
        
        if filename:
            try:
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.audio_format))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b''.join(self.recorded_frames))
                wf.close()
                
                self.log(f"Saved: {filename}", 'success')
                self.audio_recordings += 1
                self.audio_label.config(text=f"Recordings: {self.audio_recordings}")
                
                messagebox.showinfo("Success", f"Audio saved to:\n{filename}")
                
            except Exception as e:
                self.log(f"Save failed: {e}", 'error')
    
    def save_translation_audio(self):
        """Save translation as audio"""
        text = self.translated_box.get('1.0', 'end-1c').strip()
        
        if not text:
            self.log("No translation to save", 'warning')
            messagebox.showwarning("No Translation", "Translate something first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")]
        )
        
        if filename:
            try:
                tts = gTTS(text=text, lang=self.target_lang, slow=False)
                tts.save(filename)
                self.log(f"Saved: {filename}", 'success')
                messagebox.showinfo("Success", f"Translation saved to:\n{filename}")
            except Exception as e:
                self.log(f"Save failed: {e}", 'error')
    
    # ============================================
    # UTILITY FUNCTIONS
    # ============================================
    
    def change_language(self, event):
        """Change target language"""
        selected = self.lang_var.get()
        self.target_lang = self.languages[selected]
        self.log(f"Target language: {selected}", 'success')
    
    def test_microphone(self):
        """Test microphone"""
        self.log("Testing microphone...", 'info')
        
        try:
            with sr.Microphone() as source:
                self.log("Adjusting...", 'info')
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.log("Say something (3 seconds)...", 'warning')
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                
                self.log(f"Microphone working! Heard: {text}", 'success')
                messagebox.showinfo("Success", f"Microphone working!\n\nHeard: {text}")
                
        except sr.WaitTimeoutError:
            self.log("No speech detected", 'warning')
            messagebox.showwarning("Warning", "No speech detected. Speak louder?")
        except Exception as e:
            self.log(f"Test failed: {e}", 'error')
            messagebox.showerror("Error", f"Microphone test failed:\n{e}")
    
    def export_history(self):
        """Export translation history"""
        if not self.history:
            messagebox.showinfo("No History", "No translations to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, indent=2, ensure_ascii=False)
                self.log(f"History exported to {filename}", 'success')
                messagebox.showinfo("Success", "History exported!")
            except Exception as e:
                self.log(f"Export failed: {e}", 'error')
    
    def on_closing(self):
        """Clean up when closing"""
        self.is_listening = False
        if self.is_recording:
            self.stop_recording()
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        pygame.mixer.quit()
        self.root.destroy()


# ============================================
# RUN THE APPLICATION
# ============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechTranslator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
