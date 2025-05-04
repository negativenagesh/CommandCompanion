"""
Speech recognition functionality for CommandCompanion
"""

import os
import speech_recognition as sr
import threading
import time
import pyttsx3
import subprocess
import tkinter as tk
from tkinter import messagebox
from config.settings import SPEECH_CONFIG

class SpeechRecognizer:
    def __init__(self, command_callback, status_callback=None):
        """
        Initialize speech recognition with wake word detection.
        
        Args:
            command_callback: Function to call with recognized text
            status_callback: Function to update UI status (optional)
        """
        self.command_callback = command_callback
        self.status_callback = status_callback
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.is_running = False
        self.thread = None
        self.microphone = None
        
        # Get settings from config
        self.wake_word = SPEECH_CONFIG.get("wake_word", "comp").lower()
        self.sensitivity = SPEECH_CONFIG.get("sensitivity", 0.6)
        self.enable_audio_feedback = SPEECH_CONFIG.get("enable_audio_feedback", True)
        
        # Initialize text-to-speech engine if audio feedback is enabled
        if self.enable_audio_feedback:
            self.tts_engine = pyttsx3.init()
        
        # Check for microphone permission first
        if not self._check_microphone_access():
            print("Microphone access not granted. Speech recognition disabled.")
            if status_callback:
                status_callback("Error: Microphone access required")
            return
            
        # Initialize microphone after permission is granted
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise once on startup
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Ambient noise threshold adjusted")
        except Exception as e:
            print(f"Error initializing microphone: {str(e)}")
            if status_callback:
                status_callback(f"Error: {str(e)}")
    
    def _check_microphone_access(self):
        """Check if microphone access is available and request if needed"""
        try:
            # Attempt to create and use microphone
            test_mic = sr.Microphone()
            with test_mic as source:
                # Just try to get a very short recording
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=0.5)
                return True
        except OSError as e:
            if "device busy" in str(e).lower():
                print("Microphone seems to be in use by another application")
                self._show_mic_error("Microphone is being used by another application. Please close any app using the microphone and restart CommandCompanion.")
            elif "permission" in str(e).lower() or "access" in str(e).lower():
                print("Microphone permission denied")
                self._request_permission()
            else:
                print(f"Microphone error: {str(e)}")
                self._show_mic_error(f"Error accessing microphone: {str(e)}")
            return False
        except Exception as e:
            print(f"Error checking microphone: {str(e)}")
            self._show_mic_error(f"Error accessing microphone: {str(e)}")
            return False
    
    def _request_permission(self):
        """Guide the user to grant microphone permissions"""
        message = (
            "CommandCompanion needs microphone access for speech recognition.\n\n"
            "On Fedora/Linux, please:\n"
            "1. Open System Settings\n"
            "2. Go to Privacy > Microphone\n"
            "3. Enable access for CommandCompanion\n"
            "4. Restart CommandCompanion"
        )
        
        # Try to launch system settings directly
        try:
            subprocess.Popen(["gnome-control-center", "privacy"])
        except Exception:
            try:
                # Fallback for other desktop environments
                subprocess.Popen(["xdg-open", "settings://privacy"])
            except Exception:
                pass
            
        self._show_mic_error(message)
    
    def _show_mic_error(self, message):
        """Show error message to user about microphone permissions"""
        if self.status_callback:
            self.status_callback("Error: Microphone access required")
            
        # Create a separate window for the error
        try:
            dialog_root = tk.Tk()
            dialog_root.withdraw()  # Hide the main window
            messagebox.showerror("Microphone Permission Required", message)
            dialog_root.destroy()
        except Exception:
            # If we can't create a window, print to console
            print("\n" + "="*50)
            print("MICROPHONE PERMISSION REQUIRED")
            print("="*50)
            print(message)
            print("="*50 + "\n")
    
    def start_wake_detection(self):
        """Start background wake word detection"""
        if self.is_running or self.microphone is None:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._wake_detection_loop)
        self.thread.daemon = True
        self.thread.start()
        
        if self.status_callback:
            self.status_callback(f"Listening for wake word: '{self.wake_word}'...")
    
    def stop(self):
        """Stop all speech recognition"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _wake_detection_loop(self):
        """Main detection loop for wake word"""
        print(f"Wake word detection started - listening for '{self.wake_word}'")
        
        while self.is_running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, phrase_time_limit=2)
                
                # Use Sphinx for wake word detection (works offline)
                try:
                    text = self.recognizer.recognize_sphinx(audio).lower()
                    print(f"Potential wake word detected: {text}")
                    
                    # Check if wake word is in the recognized text
                    if self.wake_word in text:
                        print(f"Wake word '{self.wake_word}' detected!")
                        if not self.is_listening:
                            # Start active listening in a new thread
                            threading.Thread(target=self._listen_for_command).start()
                
                except sr.UnknownValueError:
                    # No speech detected, continue listening
                    pass
                except sr.RequestError as e:
                    print(f"Sphinx error; {e}")
            
            except Exception as e:
                print(f"Error in wake word detection: {str(e)}")
                time.sleep(1)  # Prevent tight error loop
    
    def _listen_for_command(self):
        """Listen for a command after wake word detection"""
        if self.is_listening:
            return
            
        self.is_listening = True
        
        if self.status_callback:
            self.status_callback("Listening for command...")
        
        # Audio feedback
        if self.enable_audio_feedback:
            self._speak_feedback("Yes?")
        
        try:
            with self.microphone as source:
                timeout = SPEECH_CONFIG.get("speech_recognition_timeout", 5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            if self.status_callback:
                self.status_callback("Processing speech...")
            
            # Use Google's speech recognition 
            service = SPEECH_CONFIG.get("recognition_service", "google").lower()
            
            if service == "google":
                text = self.recognizer.recognize_google(audio)
            elif service == "sphinx":
                text = self.recognizer.recognize_sphinx(audio)
            else:
                # Default to Google if unknown service
                text = self.recognizer.recognize_google(audio)
            
            if self.status_callback:
                self.status_callback(f"Recognized: {text}")
            
            print(f"Speech recognized: {text}")
            
            # Send the recognized text to the command processor
            if text and self.command_callback:
                self.command_callback(text)
        
        except sr.WaitTimeoutError:
            if self.status_callback:
                self.status_callback("Listening timed out")
            if self.enable_audio_feedback:
                self._speak_feedback("Sorry, I didn't hear anything")
        
        except sr.UnknownValueError:
            if self.status_callback:
                self.status_callback("Could not understand audio")
            if self.enable_audio_feedback:
                self._speak_feedback("Sorry, I didn't catch that")
        
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            if self.status_callback:
                self.status_callback(f"Error: {str(e)}")
        
        finally:
            self.is_listening = False
            if self.status_callback:
                self.status_callback(f"Listening for wake word: '{self.wake_word}'...")
    
    def _speak_feedback(self, text):
        """Provide audio feedback"""
        if not self.enable_audio_feedback:
            return
            
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Error in speech feedback: {str(e)}")