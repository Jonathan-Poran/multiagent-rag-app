import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Logger setup
logger = logging.getLogger("app_logger")
logger.propagate = False  # Prevent conflicts with uvicorn's logging
logger.setLevel(logging.INFO)  # Set default level

# Clear existing handlers
logger.handlers.clear()

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler with rotation (max 10MB, keep 5 backups)
file_handler = RotatingFileHandler(
    logs_dir / "app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)
logger.addHandler(console_handler)


def set_logger_level(level: str):
    """
    Set the logging level for the application logger.
    
    Args:
        level (str): The logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR').
            If an invalid level is provided, defaults to INFO.
    
    Returns:
        int: The logging level constant.
    """
    level_constant = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level_constant)
    console_handler.setLevel(level_constant)
    return level_constant


def get_logger(name: str = None):
    """
    Get a logger instance. If name is provided, returns a child logger.
    
    Args:
        name (str, optional): Name for the child logger (e.g., 'src.api').
    
    Returns:
        logging.Logger: Logger instance.
    """
    if name:
        return logger.getChild(name)
    return logger
