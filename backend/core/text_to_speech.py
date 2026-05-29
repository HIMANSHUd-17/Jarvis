"""
Text-to-Speech module for audio output
"""
import pyttsx3
import threading
from typing import Optional
from core.logger import logger
from config.settings import USE_TEXT_TO_SPEECH, TTS_SPEED

class TextToSpeech:
    def __init__(self):
        self.enabled = USE_TEXT_TO_SPEECH
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', TTS_SPEED)
        self._speaker_thread = None
    
    def speak(self, text: str, async_mode: bool = True):
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
            async_mode: If True, speak in background thread
        """
        if not self.enabled:
            logger.debug(f"TTS disabled, skipping: {text}")
            return
        
        if async_mode:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """Synchronous speech execution"""
        try:
            logger.info(f"Speaking: {text[:50]}...")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
    
    def set_voice(self, voice_id: int = 0):
        """Set voice for TTS"""
        try:
            voices = self.engine.getProperty('voices')
            if 0 <= voice_id < len(voices):
                self.engine.setProperty('voice', voices[voice_id].id)
                logger.info(f"Voice set to: {voices[voice_id].name}")
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
    
    def stop(self):
        """Stop any ongoing speech"""
        try:
            self.engine.stop()
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
