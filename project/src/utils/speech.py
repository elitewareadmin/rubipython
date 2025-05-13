"""
Speech utility module
Provides text-to-speech functionality for the application
"""
import pyttsx3
from src.utils.logger import get_logger

class SpeechManager:
    """Speech Manager class for text-to-speech functionality"""
    def __init__(self):
        self.logger = get_logger()
        self.engine = pyttsx3.init()
        # Set default properties
        self.engine.setProperty('rate', 150)    # Speaking rate
        self.engine.setProperty('volume', 0.9)  # Volume (0-1)
    
    def speak(self, text):
        """Speak the given text"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error in speech synthesis: {e}")
    
    def set_rate(self, rate):
        """Set the speaking rate (words per minute)"""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set the volume (0-1)"""
        self.engine.setProperty('volume', max(0, min(1, volume)))