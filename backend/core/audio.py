"""
Audio capture and wake-word detection module
"""
import sounddevice as sd
import numpy as np
from scipy import signal
import threading
import queue
from typing import Callable, Optional
from core.logger import logger
from config.settings import SAMPLE_RATE, CHUNK_SIZE, WAKE_WORD, WAKE_WORD_THRESHOLD

class AudioCapture:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = CHUNK_SIZE
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.wake_word = WAKE_WORD.lower()
        self.threshold = WAKE_WORD_THRESHOLD
        
    def start_listening(self):
        """Start continuous audio listening"""
        self.is_listening = True
        logger.info("Audio capture started")
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            self.audio_queue.put(indata.copy())
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            callback=audio_callback
        ):
            while self.is_listening:
                sd.sleep(100)
    
    def stop_listening(self):
        """Stop audio listening"""
        self.is_listening = False
        logger.info("Audio capture stopped")
    
    def get_audio_chunk(self):
        """Get next audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def detect_wake_word(self, audio_data: np.ndarray) -> bool:
        """
        Detect wake word in audio using frequency analysis
        This is a simplified implementation using energy detection
        """
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Normalize
        if rms > 0:
            normalized = audio_data / rms
        else:
            normalized = audio_data
        
        # Apply FFT
        fft = np.abs(np.fft.fft(normalized))
        
        # Get energy in different frequency bands
        energy_low = np.sum(fft[:100])
        energy_mid = np.sum(fft[100:500])
        energy_high = np.sum(fft[500:])
        
        # Simple heuristic: detect if there's significant speech-like energy
        total_energy = energy_low + energy_mid + energy_high
        
        if total_energy > 0:
            mid_ratio = energy_mid / total_energy
        else:
            mid_ratio = 0
        
        # Speech typically has energy concentrated in mid frequencies
        is_speech_detected = mid_ratio > self.threshold and total_energy > 100
        
        return is_speech_detected

class WakeWordDetector:
    def __init__(self, audio_capture: AudioCapture):
        self.audio_capture = audio_capture
        self.is_running = False
        self.on_wake_word: Optional[Callable] = None
        self.detector_thread = None
        
    def start(self, on_wake_word_callback: Callable):
        """Start wake word detection"""
        self.on_wake_word = on_wake_word_callback
        self.is_running = True
        self.detector_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detector_thread.start()
        logger.info(f"Wake word detector started (listening for '{self.audio_capture.wake_word}')")
    
    def stop(self):
        """Stop wake word detection"""
        self.is_running = False
        logger.info("Wake word detector stopped")
    
    def _detection_loop(self):
        """Main detection loop"""
        while self.is_running:
            chunk = self.audio_capture.get_audio_chunk()
            if chunk is not None:
                if self.audio_capture.detect_wake_word(chunk.flatten()):
                    logger.info(f"Wake word '{self.audio_capture.wake_word}' detected!")
                    if self.on_wake_word:
                        self.on_wake_word()
