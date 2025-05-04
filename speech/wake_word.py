"""
Speech recognition functionality for CommandCompanion
"""

import speech_recognition as sr
import threading
import time
import pyttsx3
from .wake_word import WakeWordDetector

class SpeechRecognizer:
    def __init__(self, command_callback, status_callback=None):
        """
        Initialize speech recognition.
        
        Args:
            command_callback: Function to call with recognized text
            status_callback: Function to update UI status (optional)
        """
        self.command_callback = command_callback
        self.status_callback = status_callback
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.wake_detector = None
        self.is_listening = False
        self.tts_engine = pyttsx3.init()
        
        # Adjust for ambient noise once on startup
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
    def start_wake_detection(self):
        """Start background wake word detection"""
        self.wake_detector = WakeWordDetector(self._wake_word_callback)
        self.wake_detector.start()
        if self.status_callback:
            self.status_callback("Listening for wake word...")
            
    def stop(self):
        """Stop all speech recognition"""
        if self.wake_detector:
            self.wake_detector.stop()
        self.is_listening = False
            
    def _wake_word_callback(self):
        """Called when wake word is detected"""
        if self.is_listening:
            return
            
        # Start active listening in a new thread
        threading.Thread(target=self._listen_for_command).start()
        
    def _listen_for_command(self):
        """Listen for a command after wake word detection"""
        self.is_listening = True
        
        if self.status_callback:
            self.status_callback("Listening for command...")
            
        # Play audio feedback to indicate listening started
        self._speak_feedback("Yes?")
        
        try:
            with self.microphone as source:
                # Shorter timeout for command
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            if self.status_callback:
                self.status_callback("Processing speech...")
                
            # Use Google's speech recognition
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
            self._speak_feedback("Sorry, I didn't hear anything")
            
        except sr.UnknownValueError:
            if self.status_callback:
                self.status_callback("Could not understand audio")
            self._speak_feedback("Sorry, I didn't catch that")
            
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            if self.status_callback:
                self.status_callback(f"Error: {str(e)}")
                
        finally:
            self.is_listening = False
            if self.status_callback:
                self.status_callback("Listening for wake word...")
    
    def _speak_feedback(self, text):
        """Provide audio feedback"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()