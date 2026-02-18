import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    """
    Configures centralized logging for the application.
    Supports both console and rotating file output.
    """
    # Ensure logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "backend.log")
    
    # Log format: [Level] [Time] [Logger] [Message]
    log_format = '%(levelname)s | %(asctime)s | %(name)s | %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Global log level from settings
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers if any
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 2. Rotating File Handler (10MB per file, keep 5 backups)
    try:
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10 * 1024 * 1024, 
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Failed to setup file logging: {e}", file=sys.stderr)

    # Set external libraries to a higher log level to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    root_logger.info(f"Logging initialized with level: {settings.LOG_LEVEL}")
