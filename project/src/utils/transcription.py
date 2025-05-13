"""
Transcription utility module
Provides speech-to-text functionality for the application
"""
import speech_recognition as sr
from src.utils.logger import get_logger

class TranscriptionManager:
    """Transcription Manager class for speech-to-text functionality"""
    def __init__(self):
        self.logger = get_logger()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def listen(self):
        """Listen and transcribe speech"""
        try:
            with self.microphone as source:
                print("Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5)
                print("Processing...")
                
                # Use Google's speech recognition
                text = self.recognizer.recognize_google(audio)
                return text.strip()
                
        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in transcription: {e}")
            return None