"""
Professional logging setup for TechJobs_Scraper_Colombia.

This module configures Python's standard logging with two handlers:
- StreamHandler: Console output at INFO level
- FileHandler: File output at DEBUG level with rotation

Log Format: [timestamp] [level] [filename:line] - message
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "techjobs") -> logging.Logger:
    """Create and configure a logger with console and file handlers.

    Args:
        name: Logger name (default: "techjobs").

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "scraper.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
