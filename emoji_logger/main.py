import inspect
import logging
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
    border_line: str = "=" * 50
    sep_line: str = "-" * 50
    date_format: str = "%Y-%m-%d %H:%M:%S"


# Enum for logging level emoji mapping
class LogEmoji(Enum):
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
            def format(self, record):
                caller_stack = inspect.stack()
                for frame_info in caller_stack:
                    frame = frame_info[0]
                    module = inspect.getmodule(frame)
                    if module and not module.__name__.startswith(
                        ("emoji_logger", "logging")
                    ):
                        record.filename = (
                            "/".join(frame_info.filename.split("/")[-3:])
                            if len(frame_info.filename.split("/")) > 3
                            else frame_info.filename
                        )
                        record.funcName = frame_info.function
                        record.lineno = frame_info.lineno
                        break
                return super().format(record)

        return CustomFormatter(
            f"{config.border_line}\n"
            f"%(asctime)s | %(levelname)s | %(name)s\n"
            f"%(filename)s | %(funcName)s | %(lineno)d\n"
            f"{config.sep_line}\n"
            "%(message)s\n"
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
    print(__file__.split("/")[-1].replace(".py", ""))
