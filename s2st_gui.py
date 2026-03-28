"""
Speech-to-Speech Translation System - GUI Version
Modern Graphical User Interface for Real-time Translation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import speech_recognition as sr
import requests
import pygame
import tempfile
import os
from gtts import gTTS
import time

class TranslationSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech-to-Speech Translation System")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Set icon (optional)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        pygame.mixer.init()
        
        # System state
        self.is_listening = False
        self.listen_thread = None
        self.target_language = "en"
        
        # Language codes
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
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the complete GUI interface"""
        
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#34495e', height=80)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="🎙️ Speech-to-Speech Translation System",
            font=('Arial', 20, 'bold'),
            bg='#34495e',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main Content Frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Control Panel
        control_frame = tk.Frame(main_frame, bg='#34495e', relief='groove', bd=2)
        control_frame.pack(fill='x', pady=10)
        
        # Language Selection
        lang_frame = tk.Frame(control_frame, bg='#34495e')
        lang_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(
            lang_frame,
            text="Target Language:",
            font=('Arial', 12),
            bg='#34495e',
            fg='white'
        ).pack(side='left', padx=5)
        
        self.lang_var = tk.StringVar(value="English")
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=list(self.languages.keys()),
            state='readonly',
            width=15
        )
        self.lang_combo.pack(side='left', padx=5)
        self.lang_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        # Status Label
        self.status_label = tk.Label(
            control_frame,
            text="⚡ System Ready",
            font=('Arial', 12),
            bg='#34495e',
            fg='#2ecc71'
        )
        self.status_label.pack(side='right', padx=20, pady=10)
        
        # Control Buttons
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            command=self.start_listening,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_listening,
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=10)
        
        self.test_button = tk.Button(
            button_frame,
            text="🎧 Test Microphone",
            command=self.test_microphone,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.test_button.pack(side='left', padx=10)
        
        # Text Display Area
        text_frame = tk.Frame(main_frame, bg='#2c3e50')
        text_frame.pack(fill='both', expand=True, pady=10)
        
        # Original Text
        tk.Label(
            text_frame,
            text="📝 Original Text:",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(anchor='w')
        
        self.original_text = scrolledtext.ScrolledText(
            text_frame,
            height=5,
            font=('Consolas', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            wrap='word'
        )
        self.original_text.pack(fill='x', pady=5)
        
        # Translated Text
        tk.Label(
            text_frame,
            text="🌐 Translated Text:",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(anchor='w', pady=(10,0))
        
        self.translated_text = scrolledtext.ScrolledText(
            text_frame,
            height=5,
            font=('Consolas', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            wrap='word'
        )
        self.translated_text.pack(fill='x', pady=5)
        
        # Status Log
        tk.Label(
            text_frame,
            text="📋 Status Log:",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(anchor='w', pady=(10,0))
        
        self.log_text = scrolledtext.ScrolledText(
            text_frame,
            height=6,
            font=('Consolas', 10),
            bg='#34495e',
            fg='#ecf0f1',
            wrap='word'
        )
        self.log_text.pack(fill='x', pady=5)
        
        # Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready | Target: English",
            bd=1,
            relief='sunken',
            anchor='w',
            bg='#34495e',
            fg='white'
        )
        self.status_bar.pack(side='bottom', fill='x')
        
    def log_message(self, message, color='white'):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        
    def change_language(self, event=None):
        """Change target translation language"""
        self.target_language = self.languages[self.lang_var.get()]
        self.status_bar.config(text=f"Ready | Target: {self.lang_var.get()}")
        self.log_message(f"Target language changed to: {self.lang_var.get()}")
        
    def translate_text(self, text):
        """Translate text using Google Translate API"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
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
            self.log_message(f"Translation error: {e}", 'red')
        
        return text
    
    def speak_text(self, text):
        """Convert text to speech and play"""
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
            self.log_message(f"Speech error: {e}", 'red')
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def process_speech(self, audio):
        """Process speech: recognize, translate, and speak"""
        try:
            # Convert to text
            text = self.recognizer.recognize_google(audio)
            self.log_message(f"✅ Recognized: {text}", '#2ecc71')
            
            # Update original text
            self.original_text.delete('1.0', 'end')
            self.original_text.insert('1.0', text)
            
            # Translate
            translated = self.translate_text(text)
            self.log_message(f"🔄 Translated: {translated}", '#3498db')
            
            # Update translated text
            self.translated_text.delete('1.0', 'end')
            self.translated_text.insert('1.0', translated)
            
            # Speak
            self.log_message(f"🔊 Speaking translation...", '#f39c12')
            self.speak_text(translated)
            self.log_message(f"✅ Done!", '#2ecc71')
            
        except sr.UnknownValueError:
            self.log_message("❌ Could not understand audio", '#e74c3c')
        except sr.RequestError as e:
            self.log_message(f"❌ Network error: {e}", '#e74c3c')
        except Exception as e:
            self.log_message(f"❌ Error: {e}", '#e74c3c')
    
    def listen_continuous(self):
        """Continuous listening loop"""
        try:
            with sr.Microphone() as source:
                self.log_message("🎤 Calibrating microphone...", '#f39c12')
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.log_message("✅ Ready! Listening...", '#2ecc71')
                
                while self.is_listening:
                    try:
                        self.status_label.config(text="🎤 Listening...", fg='#f39c12')
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        if audio and self.is_listening:
                            self.process_speech(audio)
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        self.log_message(f"Error: {e}", '#e74c3c')
                        
        except Exception as e:
            self.log_message(f"Microphone error: {e}", '#e74c3c')
        finally:
            if not self.is_listening:
                self.root.after(0, self.reset_ui)
    
    def start_listening(self):
        """Start listening in separate thread"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="🎤 Listening...", fg='#f39c12')
        
        self.listen_thread = threading.Thread(target=self.listen_continuous)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        self.log_message("🚀 Started continuous listening mode", '#2ecc71')
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.log_message("⏹️ Stopped listening", '#e74c3c')
    
    def reset_ui(self):
        """Reset UI after stopping"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="⚡ System Ready", fg='#2ecc71')
    
    def test_microphone(self):
        """Test microphone functionality"""
        self.log_message("Testing microphone...", '#3498db')
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.log_message("Say something for test...", '#f39c12')
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                
                self.log_message(f"✅ Microphone working! Heard: {text}", '#2ecc71')
                messagebox.showinfo("Success", f"Microphone working!\n\nHeard: {text}")
                
        except sr.WaitTimeoutError:
            self.log_message("⚠️ No speech detected", '#f39c12')
            messagebox.showwarning("Warning", "No speech detected. Please speak louder.")
        except Exception as e:
            self.log_message(f"❌ Microphone test failed: {e}", '#e74c3c')
            messagebox.showerror("Error", f"Microphone test failed:\n{e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationSystemGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
