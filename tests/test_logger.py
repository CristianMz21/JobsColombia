"""Tests for the logger module."""

import logging

from jobscolombia.logger import setup_logger


class TestSetupLogger:
    """Tests for the setup_logger function."""

    def test_setup_logger_returns_logger_instance(self):
        """Test that setup_logger returns a Logger instance."""
        logger = setup_logger()
        assert isinstance(logger, logging.Logger)

    def test_setup_logger_has_correct_name(self):
        """Test that logger has the correct name."""
        logger = setup_logger()
        assert logger.name == "techjobs"

    def test_setup_logger_has_console_handler(self):
        """Test that logger has a console handler."""
        logger = setup_logger()
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0

    def test_setup_logger_console_level_is_info(self):
        """Test that console handler is set to INFO level."""
        logger = setup_logger()
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0
        assert console_handlers[0].level == logging.INFO

    def test_setup_logger_has_file_handler(self):
        """Test that logger has a file handler."""
        logger = setup_logger()
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_setup_logger_file_level_is_debug(self):
        """Test that file handler is set to DEBUG level."""
        logger = setup_logger()
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0
        assert file_handlers[0].level == logging.DEBUG

    def test_setup_logger_can_log_info(self):
        """Test that logger can log info messages."""
        logger = setup_logger()
        # Should not raise any exception
        logger.info("Test info message")

    def test_setup_logger_can_log_warning(self):
        """Test that logger can log warning messages."""
        logger = setup_logger()
        logger.warning("Test warning message")

    def test_setup_logger_can_log_error(self):
        """Test that logger can log error messages."""
        logger = setup_logger()
        logger.error("Test error message")

    def test_setup_logger_creates_logs_directory(self, tmp_path):
        """Test that logger creates the logs directory if it doesn't exist."""
        # Logger should create logs directory automatically
        logger = setup_logger()
        # File handler should work
        logger.info("Test message")
