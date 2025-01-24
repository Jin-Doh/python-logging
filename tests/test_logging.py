import logging
import re
from io import StringIO
from pathlib import Path

import pytest

from emoji_logger import LogConfig, LogEmoji, Logger


@pytest.fixture
def temp_log_file(tmp_path):
    return tmp_path / "test.log"


@pytest.fixture
def custom_config():
    return LogConfig(
        border_line="*" * 30,
        sep_line="-" * 30,
        date_format="%Y-%m-%d",
    )


@pytest.fixture
def string_buffer():
    return StringIO()


def test_log_levels():
    test_cases = [
        ("DEBUG", ["debug", "info", "warning", "error", "critical"]),
        ("INFO", ["info", "warning", "error", "critical"]),
        ("WARNING", ["warning", "error", "critical"]),
        ("ERROR", ["error", "critical"]),
        ("CRITICAL", ["critical"]),
    ]

    for level, expected_logs in test_cases:
        logger = Logger(f"test_{level.lower()}", level)
        for log_level in expected_logs:
            getattr(logger, log_level)(f"Test {log_level} message")
        # Try logging all levels
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

        # Validate log level
        assert logger.logger.getEffectiveLevel() == getattr(logging, level)


def test_invalid_log_level():
    # Test with invalid string level
    logger = Logger("test_invalid", "INVALID_LEVEL")
    assert logger.logger.getEffectiveLevel() == logging.INFO

    # Test with valid integer level
    logger = Logger("test_valid", logging.DEBUG)
    assert logger.logger.getEffectiveLevel() == logging.DEBUG


def test_file_logging(temp_log_file: Path):
    logger = Logger(
        name="test_file",
        level="DEBUG",
        is_save=True,
        log_path=str(temp_log_file),
    )
    test_message = "Test file logging"
    logger.info(test_message)

    assert temp_log_file.exists()
    with open(temp_log_file) as f:
        content = f.read()
        assert test_message in content
        # Check if the log contains all required components
        assert logger.config.border_line in content
        assert logger.config.sep_line in content
        assert "test_file" in content  # logger name
        assert "INFO" in content  # log level


def test_file_logging_directory_creation(tmp_path):
    log_dir = tmp_path / "logs"
    log_file = log_dir / "test.log"

    _ = Logger(
        name="test_dir_creation",
        level="DEBUG",
        is_save=True,
        log_path=str(log_file),
    )

    assert log_dir.exists()
    assert log_dir.is_dir()


def test_file_logging_missing_path():
    with pytest.raises(
        ValueError,
        match="log_path is required when is_save is True",
    ):
        Logger(name="test_missing_path", is_save=True)


def test_custom_config(custom_config):
    logger = Logger("test_custom", "DEBUG", config=custom_config)

    assert logger.config.border_line == "*" * 30
    assert logger.config.sep_line == "-" * 30
    assert logger.config.date_format == "%Y-%m-%d"


def test_duplicate_filter(string_buffer):
    # Create a logger with our string buffer
    logger = Logger("test_duplicate")
    # Replace the stream handler's stream with our buffer
    logger.console_handler.stream = string_buffer

    test_message = "Duplicate message"

    # Log same message multiple times
    logger.info(test_message)
    logger.info(test_message)
    logger.info(test_message)

    # Get output
    output = string_buffer.getvalue()

    # Count occurrences of the test message
    message_count = output.count(test_message)
    assert message_count == 1, "Duplicate message was not filtered"


def test_log_emoji_mapping():
    # Test all emoji mappings
    for level_name in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        assert hasattr(LogEmoji, level_name)
        emoji = LogEmoji[level_name].value
        assert isinstance(emoji, str)
        assert len(emoji) > 0


def test_caller_location_tracking(string_buffer):
    def inner_function():
        logger.info("Test caller tracking")

    # Create logger with our string buffer
    logger = Logger("test_caller")
    logger.console_handler.stream = string_buffer

    inner_function()

    # Get output
    output = string_buffer.getvalue()

    # Verify that the log contains the correct caller information
    if not output.startswith("===="):  # pytest-related
        assert "test_caller" in output  # logger name
        assert "test_logging.py" in output  # filename
        assert "inner_function" in output  # function name


def test_log_formatting(string_buffer):
    # Create logger with our string buffer
    logger = Logger("test_format")
    logger.console_handler.stream = string_buffer

    test_message = "Test formatting"
    logger.info(test_message)

    # Get output
    output = string_buffer.getvalue()

    # Check all required components are present
    assert logger.config.border_line in output
    assert logger.config.sep_line in output
    assert test_message in output
    assert "INFO" in output
    assert "test_format" in output

    # Check date format
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    assert re.search(date_pattern, output) is not None


if __name__ == "__main__":
    pytest.main([__file__])
