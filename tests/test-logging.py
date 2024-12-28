import logging
from pathlib import Path

import pytest

from emoji_logger import LogConfig, Logger


@pytest.fixture
def temp_log_file(tmp_path):
    return tmp_path / "test.log"


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


def test_custom_config():
    custom_config = LogConfig(
        border_line="*" * 30, sep_line="-" * 30, date_format="%Y-%m-%d"
    )
    logger = Logger("test_custom", "DEBUG", config=custom_config)
    logger.info("Test custom config")
    # In this case, we are not checking the output format,
    # but only checking if the logger is created successfully
    assert logger.config.border_line == "*" * 30


def test_duplicate_filter():
    logger = Logger("test_duplicate")
    test_message = "Duplicate message"

    # Test duplicate message
    logger.info(test_message)
    logger.info(test_message)
    # Duplicate filtering will filter out the second message
    # Check if the logger is working properly


if __name__ == "__main__":
    pytest.main([__file__])
