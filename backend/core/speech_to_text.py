"""
Speech-to-Text module using Whisper
"""
import whisper
import numpy as np
import sounddevice as sd
from typing import Optional
import threading
from core.logger import logger
from config.settings import WHISPER_MODEL, USE_GPU, SAMPLE_RATE

class SpeechToText:
    def __init__(self):
        self.model = None
        self.device = "cuda" if USE_GPU else "cpu"
        self.sample_rate = SAMPLE_RATE
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL} on {self.device}")
            self.model = whisper.load_model(WHISPER_MODEL, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_file(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio from file"""
        try:
            result = self.model.transcribe(audio_file_path, language="en", fp16=False)
            text = result.get("text", "").strip()
            logger.info(f"Transcribed text: {text}")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def transcribe_audio_data(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe audio from numpy array"""
        try:
            # Normalize audio data
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            result = self.model.transcribe(audio_data, language="en", fp16=False)
            text = result.get("text", "").strip()
            logger.info(f"Transcribed text: {text}")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def record_and_transcribe(self, duration: int = 10) -> Optional[str]:
        """Record audio and transcribe in real-time"""
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            audio_data = sd.rec(
                int(self.sample_rate * duration),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            
            audio_data = audio_data.flatten()
            return self.transcribe_audio_data(audio_data)
        except Exception as e:
            logger.error(f"Record and transcribe error: {e}")
            return None
