"""
Speech-to-Speech Translation System - Professional Edition
Modern GUI with Advanced Features for Real-time Translation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import speech_recognition as sr
import requests
import pygame
import tempfile
import os
import time
import json
from datetime import datetime
from gtts import gTTS
import wave
import numpy as np

class ProfessionalTranslationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SpeechMaster Pro - Real-Time Translation System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Set modern style
        self.setup_styles()
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        
        # System state
        self.is_listening = False
        self.listen_thread = None
        self.target_language = "en"
        self.source_language = "auto"
        self.history = []
        
        # Language database
        self.languages = {
            "English": {"code": "en", "flag": "🇺🇸", "voice": "en"},
            "Hindi": {"code": "hi", "flag": "🇮🇳", "voice": "hi"},
            "Spanish": {"code": "es", "flag": "🇪🇸", "voice": "es"},
            "French": {"code": "fr", "flag": "🇫🇷", "voice": "fr"},
            "German": {"code": "de", "flag": "🇩🇪", "voice": "de"},
            "Japanese": {"code": "ja", "flag": "🇯🇵", "voice": "ja"},
            "Chinese": {"code": "zh", "flag": "🇨🇳", "voice": "zh"},
            "Arabic": {"code": "ar", "flag": "🇸🇦", "voice": "ar"},
            "Russian": {"code": "ru", "flag": "🇷🇺", "voice": "ru"},
            "Italian": {"code": "it", "flag": "🇮🇹", "voice": "it"},
            "Portuguese": {"code": "pt", "flag": "🇵🇹", "voice": "pt"},
            "Korean": {"code": "ko", "flag": "🇰🇷", "voice": "ko"}
        }
        
        self.setup_ui()
        
    def setup_styles(self):
        """Setup modern styles for widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'bg': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#0f3460',
            'success': '#00d4ff',
            'warning': '#ff6b6b',
            'text': '#ffffff',
            'text_secondary': '#b8b8b8'
        }
        
    def setup_ui(self):
        """Setup the complete professional UI"""
        
        # Main Container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Top Header with Gradient Effect
        header_frame = tk.Frame(main_container, bg=self.colors['secondary'], height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Logo and Title
        title_frame = tk.Frame(header_frame, bg=self.colors['secondary'])
        title_frame.pack(side='left', padx=30, pady=20)
        
        tk.Label(
            title_frame,
            text="🎙️ SpeechMaster Pro",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['success']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Real-Time Speech Translation System",
            font=('Segoe UI', 11),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w')
        
        # Status Indicator
        status_frame = tk.Frame(header_frame, bg=self.colors['secondary'])
        status_frame.pack(side='right', padx=30, pady=20)
        
        self.status_indicator = tk.Canvas(
            status_frame,
            width=12,
            height=12,
            bg=self.colors['secondary'],
            highlightthickness=0
        )
        self.status_indicator.pack(side='left', padx=5)
        self.status_indicator.create_oval(2, 2, 10, 10, fill='#2ecc71', outline='')
        
        self.status_text = tk.Label(
            status_frame,
            text="System Ready",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['success']
        )
        self.status_text.pack(side='left')
        
        # Main Content Area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left Panel - Controls
        left_panel = tk.Frame(content_frame, bg=self.colors['secondary'], width=280)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Control Buttons
        self.setup_control_panel(left_panel)
        
        # Right Panel - Main Content
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Text Display Area
        self.setup_text_display(right_panel)
        
        # Bottom Status Bar
        self.setup_status_bar(main_container)
        
    def setup_control_panel(self, parent):
        """Setup control panel with all controls"""
        
        # Logo/Icon
        tk.Label(
            parent,
            text="🎙️",
            font=('Segoe UI', 48),
            bg=self.colors['secondary'],
            fg=self.colors['success']
        ).pack(pady=20)
        
        # Action Buttons
        button_frame = tk.Frame(parent, bg=self.colors['secondary'])
        button_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Translation",
            command=self.start_listening,
            font=('Segoe UI', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            width=20,
            cursor='hand2',
            relief='flat'
        )
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_listening,
            font=('Segoe UI', 12),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            width=20,
            state='disabled',
            cursor='hand2',
            relief='flat'
        )
        self.stop_btn.pack(pady=5)
        
        self.test_btn = tk.Button(
            button_frame,
            text="🎧 Test Microphone",
            command=self.test_microphone,
            font=('Segoe UI', 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            width=20,
            cursor='hand2',
            relief='flat'
        )
        self.test_btn.pack(pady=5)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=15)
        
        # Language Settings
        tk.Label(
            parent,
            text="Translation Settings",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        ).pack(pady=(10, 5))
        
        # Source Language
        tk.Label(
            parent,
            text="Source Language:",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', padx=20)
        
        self.source_var = tk.StringVar(value="Auto Detect")
        source_combo = ttk.Combobox(
            parent,
            textvariable=self.source_var,
            values=["Auto Detect"] + list(self.languages.keys()),
            state='readonly',
            width=25
        )
        source_combo.pack(pady=5, padx=20)
        source_combo.bind('<<ComboboxSelected>>', self.change_source_language)
        
        # Target Language
        tk.Label(
            parent,
            text="Target Language:",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        ).pack(anchor='w', padx=20, pady=(10,0))
        
        self.target_var = tk.StringVar(value="English")
        target_combo = ttk.Combobox(
            parent,
            textvariable=self.target_var,
            values=list(self.languages.keys()),
            state='readonly',
            width=25
        )
        target_combo.pack(pady=5, padx=20)
        target_combo.bind('<<ComboboxSelected>>', self.change_target_language)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=15)
        
        # Stats
        tk.Label(
            parent,
            text="Session Stats",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        ).pack(pady=(10, 5))
        
        self.translation_count = tk.Label(
            parent,
            text="Translations: 0",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        self.translation_count.pack(anchor='w', padx=20)
        
        self.session_time = tk.Label(
            parent,
            text="Session: 0s",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        self.session_time.pack(anchor='w', padx=20, pady=(5, 0))
        
        # Export Button
        export_btn = tk.Button(
            parent,
            text="📥 Export History",
            command=self.export_history,
            font=('Segoe UI', 10),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=5,
            width=20,
            cursor='hand2',
            relief='flat'
        )
        export_btn.pack(pady=(20, 5))
        
    def setup_text_display(self, parent):
        """Setup text display area with tabs"""
        
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1 - Translation Display
        translation_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(translation_tab, text="📝 Translation")
        
        # Original Text
        tk.Label(
            translation_tab,
            text="🔊 Original Text",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(anchor='w', pady=(10, 5))
        
        self.original_text = scrolledtext.ScrolledText(
            translation_tab,
            height=6,
            font=('Segoe UI', 11),
            bg='#2d2d3a',
            fg='#ffffff',
            wrap='word',
            insertbackground='white'
        )
        self.original_text.pack(fill='x', pady=5, padx=5)
        
        # Translated Text
        tk.Label(
            translation_tab,
            text="🌐 Translated Text",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(anchor='w', pady=(15, 5))
        
        self.translated_text = scrolledtext.ScrolledText(
            translation_tab,
            height=6,
            font=('Segoe UI', 11),
            bg='#2d2d3a',
            fg='#ffffff',
            wrap='word',
            insertbackground='white'
        )
        self.translated_text.pack(fill='x', pady=5, padx=5)
        
        # Tab 2 - History Log
        history_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(history_tab, text="📜 History")
        
        self.history_text = scrolledtext.ScrolledText(
            history_tab,
            font=('Consolas', 10),
            bg='#2d2d3a',
            fg='#b8b8b8',
            wrap='word'
        )
        self.history_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 3 - System Log
        log_tab = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(log_tab, text="⚡ System Log")
        
        self.log_text = scrolledtext.ScrolledText(
            log_tab,
            font=('Consolas', 10),
            bg='#2d2d3a',
            fg='#b8b8b8',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_status_bar(self, parent):
        """Setup bottom status bar"""
        status_bar = tk.Frame(parent, bg=self.colors['secondary'], height=30)
        status_bar.pack(side='bottom', fill='x')
        status_bar.pack_propagate(False)
        
        self.status_message = tk.Label(
            status_bar,
            text="✅ System initialized | Ready for translation",
            font=('Segoe UI', 9),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        self.status_message.pack(side='left', padx=10, pady=5)
        
        # Current time
        self.time_label = tk.Label(
            status_bar,
            text=datetime.now().strftime("%H:%M:%S"),
            font=('Segoe UI', 9),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        self.time_label.pack(side='right', padx=10, pady=5)
        self.update_time()
        
    def update_time(self):
        """Update time display"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
        
    def log_message(self, message, msg_type='info'):
        """Add message to log with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            'info': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'error': '#e74c3c'
        }
        
        self.log_text.insert('end', f"[{timestamp}] ", colors['info'])
        self.log_text.insert('end', f"{message}\n", colors.get(msg_type, '#ffffff'))
        self.log_text.see('end')
        
        # Update status bar for important messages
        if msg_type == 'success':
            self.status_message.config(text=f"✅ {message}")
        elif msg_type == 'error':
            self.status_message.config(text=f"❌ {message}")
        
    def change_source_language(self, event):
        """Change source language"""
        selected = self.source_var.get()
        if selected == "Auto Detect":
            self.source_language = "auto"
            self.log_message(f"Source language set to: Auto Detect", 'info')
        else:
            self.source_language = self.languages[selected]["code"]
            self.log_message(f"Source language set to: {selected}", 'info')
    
    def change_target_language(self, event):
        """Change target language"""
        selected = self.target_var.get()
        self.target_language = self.languages[selected]["code"]
        self.log_message(f"Target language set to: {selected} {self.languages[selected]['flag']}", 'success')
        
    def translate_text(self, text):
        """Translate text using Google Translate API"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': self.source_language,
                'tl': self.target_language,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and data[0]:
                    translated = ''.join([s[0] for s in data[0]])
                    return translated
        except Exception as e:
            self.log_message(f"Translation error: {e}", 'error')
        
        return text
    
    def speak_text(self, text):
        """Convert text to speech with pitch control"""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            tts = gTTS(text=text, lang=self.target_language, slow=False)
            tts.save(temp_file.name)
            
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except Exception as e:
            self.log_message(f"Speech error: {e}", 'error')
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def process_speech(self, audio):
        """Process speech through the pipeline"""
        try:
            # Convert to text
            text = self.recognizer.recognize_google(audio)
            self.log_message(f"Recognized: {text}", 'success')
            
            # Update original text
            self.original_text.delete('1.0', 'end')
            self.original_text.insert('1.0', text)
            
            # Translate
            translated = self.translate_text(text)
            self.log_message(f"Translated: {translated}", 'info')
            
            # Update translated text
            self.translated_text.delete('1.0', 'end')
            self.translated_text.insert('1.0', translated)
            
            # Add to history
            self.add_to_history(text, translated)
            
            # Speak
            self.log_message(f"Speaking translation...", 'info')
            self.speak_text(translated)
            
            # Update stats
            self.update_stats()
            
        except sr.UnknownValueError:
            self.log_message("Could not understand audio", 'warning')
        except sr.RequestError as e:
            self.log_message(f"Network error: {e}", 'error')
        except Exception as e:
            self.log_message(f"Error: {e}", 'error')
    
    def add_to_history(self, original, translated):
        """Add translation to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Original: {original}\n          Translation: {translated}\n{'-'*50}\n"
        self.history_text.insert('end', entry)
        self.history_text.see('end')
        self.history.append({
            'timestamp': timestamp,
            'original': original,
            'translated': translated
        })
    
    def update_stats(self):
        """Update translation statistics"""
        count = len(self.history)
        self.translation_count.config(text=f"Translations: {count}")
    
    def export_history(self):
        """Export translation history to file"""
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
                self.log_message(f"History exported to {filename}", 'success')
                messagebox.showinfo("Success", "History exported successfully!")
            except Exception as e:
                self.log_message(f"Export failed: {e}", 'error')
    
    def listen_continuous(self):
        """Continuous listening loop"""
        try:
            with sr.Microphone() as source:
                self.log_message("Calibrating microphone...", 'info')
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.log_message("Ready! Listening for speech...", 'success')
                
                while self.is_listening:
                    try:
                        self.status_indicator.itemconfig(1, fill='#f39c12')
                        self.status_text.config(text="Listening...", fg='#f39c12')
                        
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                        
                        if audio and self.is_listening:
                            self.process_speech(audio)
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        if self.is_listening:
                            self.log_message(f"Error: {e}", 'error')
                        
        except Exception as e:
            self.log_message(f"Microphone error: {e}", 'error')
        finally:
            if not self.is_listening:
                self.root.after(0, self.reset_ui)
    
    def start_listening(self):
        """Start listening in separate thread"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.listen_thread = threading.Thread(target=self.listen_continuous)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.log_message("Started continuous translation mode", 'success')
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.log_message("Stopped listening", 'warning')
    
    def reset_ui(self):
        """Reset UI after stopping"""
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_indicator.itemconfig(1, fill='#2ecc71')
        self.status_text.config(text="System Ready", fg='#2ecc71')
    
    def test_microphone(self):
        """Test microphone functionality"""
        self.log_message("Testing microphone...", 'info')
        
        try:
            with sr.Microphone() as source:
                self.log_message("Adjusting for ambient noise...", 'info')
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.log_message("Say something for test (5 seconds)...", 'warning')
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                
                self.log_message(f"Microphone working! Heard: {text}", 'success')
                messagebox.showinfo("Success", f"Microphone is working!\n\nHeard: {text}")
                
        except sr.WaitTimeoutError:
            self.log_message("No speech detected", 'warning')
            messagebox.showwarning("Warning", "No speech detected. Please speak louder.")
        except Exception as e:
            self.log_message(f"Microphone test failed: {e}", 'error')
            messagebox.showerror("Error", f"Microphone test failed:\n\n{e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalTranslationGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
