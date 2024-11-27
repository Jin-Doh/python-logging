import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from emoji_logger import Logger

def test_debug_lv():
    logger = Logger("test_debug_lv", "DEBUG")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")

def test_info_lv():
    logger = Logger("test_info_lv", "INFO")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")

def test_warning_lv():
    logger = Logger("test_warning_lv", "WARNING")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")

def test_error_lv():
    logger = Logger("test_error_lv", "ERROR")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")

def test_critical_lv():
    logger = Logger("test_critical_lv", "CRITICAL")
    logger.logger.debug("This is a debug message")
    logger.logger.info("This is an info message")
    logger.logger.warning("This is a warning message")
    logger.logger.error("This is an error message")
    logger.logger.critical("This is a critical message")

if __name__ == "__main__":
    test_debug_lv()
    test_info_lv()
    test_warning_lv()
    test_error_lv()
    test_critical_lv()
