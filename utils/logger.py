"""
Centralized logging configuration using loguru
"""
import sys
import os
from loguru import logger
from config.settings import settings

# Remove default handler
logger.remove()

# Console handler with color
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# File handler with rotation
os.makedirs("logs", exist_ok=True)
logger.add(
    settings.LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    compression="zip",
    serialize=False,
)

# Error-only file
logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
)

def get_logger(name: str = __name__):
    """Get logger instance with custom name"""
    return logger.bind(name=name)

# Export logger
__all__ = ["logger", "get_logger"]
