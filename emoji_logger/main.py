import inspect
import logging
import os
import sys
import traceback
from dataclasses import dataclass
from enum import Enum
from logging import FileHandler, StreamHandler
from pathlib import Path
from typing import Any


# dataclass for logging configuration
@dataclass
class LogConfig:
    """
    Configuration settings for log formatting.

    Attributes:
        border_line (str): A constant string consisting of 50 equal signs \
            ('=' * 50) used to render a border line in log outputs.
        sep_line (str): A constant string consisting of 50 hyphens \
            ('-' * 50) used as a separator line in log messages.
        date_format (str): A format string ("%Y-%m-%d %H:%M:%S") \
            defining the date and time structure for log entries.
    """

    border_line: str = "=" * 50
    sep_line: str = "-" * 50
    date_format: str = "%Y-%m-%d %H:%M:%S"


# Enum for logging level emoji mapping
class LogEmoji(Enum):
    """
    Enumeration of emoji representations for different logging levels.

    Attributes:
        DEBUG (str): Emoji representing the debug level (🛠️)
        INFO (str): Emoji representing the informational level (📚)
        WARNING (str): Emoji representing the warning level (🔥)
        ERROR (str): Emoji representing the error level (⛔️)
        CRITICAL (str): Emoji representing the critical level (❌)
        DEFAULT (str): Default emoji used when no specific level is matched (❓)
    """

    DEBUG = "🛠️"
    INFO = "📚"
    WARNING = "🔥"
    ERROR = "⛔️"
    CRITICAL = "❌"
    DEFAULT = "❓"


class DuplicateFilter(logging.Filter):
    """
    Filter class to remove duplicate logs.
    It filters out logs with the same message and level.
    """

    def __init__(self):
        super().__init__()
        self.last_log = None

    def filter(self, record):
        current_hash = hash((record.levelname, record.getMessage()))
        if current_hash != self.last_log:
            self.last_log = current_hash
            return True
        return False


class Logger:
    """
    Logger class for logging messages to console.
    This class is a wrapper around the logging module.

    :param name: str: Name of the logger
    :param level: str | int: Logging level (default: logging.DEBUG)
    :param is_save: bool: Save log to file (default: False)
    :param log_path: str | None: Path to save log file (default: None)
    :param config: LogConfig | None: Logging configuration (default: None)
    """

    def __init__(
        self,
        name: str,
        level: str | int = logging.DEBUG,
        is_save: bool = False,
        log_path: str | None = None,
        config: LogConfig | None = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_level(level))
        self.config = config or LogConfig()
        self._set_stream_handler()
        if is_save:
            if not log_path:
                raise ValueError("log_path is required when is_save is True")
            self.log_path = Path(log_path)
            self._set_file_handler()

    def _set_stream_handler(self):
        self.console_handler = StreamHandler(stream=sys.stdout)
        self.console_handler.setFormatter(Logger._get_formatter())
        self.logger.addHandler(self.console_handler)
        self.logger.addFilter(DuplicateFilter())

    def _set_file_handler(self):
        if not self.log_path.parent.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_handler = FileHandler(self.log_path, encoding="utf-8")
        self.file_handler.setFormatter(Logger._get_formatter())
        self.logger.addHandler(self.file_handler)
        self.logger.addFilter(DuplicateFilter())

    def _get_level(self, lv: int | str) -> int:
        if isinstance(lv, str):
            lv = lv.upper()
            match lv:
                case "DEBUG":
                    return logging.DEBUG
                case "INFO":
                    return logging.INFO
                case "WARNING":
                    return logging.WARNING
                case "ERROR":
                    return logging.ERROR
                case "CRITICAL":
                    return logging.CRITICAL
                case _:
                    log_msg = f"Invalid log level: {lv}. Using INFO level."
                    self.logger.warning(log_msg)
                    return logging.INFO
        return lv

    @staticmethod
    def _get_emoji(level: int | str) -> str:
        if isinstance(level, int):
            level = logging.getLevelName(level)
        try:
            return LogEmoji[level].value
        except KeyError:
            return LogEmoji.DEFAULT.value

    @staticmethod
    def _get_formatter(config: LogConfig = LogConfig()):
        class CustomFormatter(logging.Formatter):
            """
            A custom logging formatter that extends logging.Formatter \
                to enhance log records with caller information.

            This formatter overrides the default format() method.
            When a log record is formatted, it:
                - Retrieves the current call stack using the inspect module.
                - Iterates through the stack frames \
                    (skipping the frame for the current function).
                - Filters out frames associated with the current logger module\
                    (the module in which this formatter is defined),
                    as well as those starting with "logging" or "pytest".
                - Once a suitable caller frame is found, \
                    updates the log record's 'filename', 'funcName', 'lineno' \
                    attributes with the corresponding values \
                        (i.e., the basename of the file, function name,
                        and line number where the logging call was made).
                - Returns the original formatted message \
                    generated by the base class.

            This approach is useful for dynamically determining \
                the calling location in the code,
            which can aid in debugging by providing more precise information \
                about where each log message originates.
            """

            def format(self, record):
                original_format = super().format(record)
                try:
                    stack = inspect.stack()
                    # 전달 받은 stacklevel 값이 있으면 그만큼 건너뛰도록 함 (기본값 2)
                    start_index = record.__dict__.get("stacklevel", 2)
                    logger_module = __name__

                    for frame_info in stack[start_index:]:
                        frame = frame_info.frame
                        frame_module = frame.f_globals.get("__name__", "")
                        if any(
                            [
                                frame_module == logger_module,
                                frame_module.startswith("logging"),
                                frame_module.startswith("pytest"),
                            ]
                        ):
                            continue

                        record.filename = os.path.basename(frame_info.filename)
                        record.funcName = frame_info.function
                        record.lineno = frame_info.lineno
                        break

                except Exception as e:
                    print(f"Error getting caller info: {e}")

                return original_format

        return CustomFormatter(
            f"{config.border_line}\n"
            f"%(asctime)s | %(levelname)s | %(name)s\n"
            f"%(filename)s | %(funcName)s | %(lineno)d\n"
            f"{config.sep_line}\n"
            f"%(message)s\n"
            f"{config.border_line}",
            datefmt=config.date_format,
        )

    @staticmethod
    def handle_exception(msg: str | Exception) -> str:
        """Handle exceptions and return formatted message"""
        try:
            if not traceback.format_exc().startswith("NoneType: None"):
                if isinstance(msg, Exception):
                    return f"{str(msg)}\n{traceback.format_exc()}"
                return f"{msg}\n{traceback.format_exc()}"
            return str(msg)
        except TypeError:
            return str(msg)

    @staticmethod
    def handle_msg(level: int, msg: Any) -> str:
        """Handle messages and return formatted message"""
        caller = inspect.stack()[2].function
        caller = "main" if caller == "<module>" else caller

        if level in (logging.ERROR, logging.CRITICAL):
            msg = Logger.handle_exception(msg)
        return f"{Logger._get_emoji(level)} | {caller} | {msg}"

    def debug(self, msg: object):
        "logging debug messages"
        self.logger.debug(self.handle_msg(logging.DEBUG, msg))

    def info(self, msg: object):
        "logging info messages"
        self.logger.info(self.handle_msg(logging.INFO, msg))

    def warning(self, msg: object):
        "logging warning messages"
        self.logger.warning(self.handle_msg(logging.WARNING, msg))

    def error(self, msg: object):
        "logging error messages"
        self.logger.error(self.handle_msg(logging.ERROR, msg))

    def critical(self, msg: object):
        "logging critical messages"
        self.logger.critical(self.handle_msg(logging.CRITICAL, msg))


logger = Logger(name="MAIN", level=logging.INFO, is_save=False)

if __name__ == "__main__":
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
