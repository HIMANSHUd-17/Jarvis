"""
Logging configuration for JARVIS
"""
import logging
import logging.handlers
import os
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT

# Ensure logs directory exists
Path(os.path.dirname(LOG_FILE)).mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Configure logging for the entire application"""
    logger = logging.getLogger("jarvis")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()
