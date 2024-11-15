"This module contains the Logger class for logging messages to console"
import os
import sys
import inspect
import logging
import traceback
from typing import Union

class Logger:
    """
    Logger class for logging messages to console.
    This class is a wrapper around the logging module.

    :param name: str: Name of the logger
    :param level: Union[str, int]: Logging level (default: logging.DEBUG)
    """

    def __init__(self, name: str, level: Union[str, int] = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_level(level))
        self.console_handler = logging.StreamHandler(stream=sys.stdout)
        self.console_handler.setFormatter(Logger._get_formatter())
        self.logger.addHandler(self.console_handler)

    def _get_level(self, lv: Union[int, str]):
        if isinstance(lv, str):
            lv = lv.upper()
        if lv == "DEBUG":
            return logging.DEBUG
        elif lv == "INFO":
            return logging.INFO
        elif lv == "WARNING":
            return logging.WARNING
        elif lv == "ERROR":
            return logging.ERROR
        elif lv == "CRITICAL":
            return logging.CRITICAL
        else:
            return logging.DEBUG

    @staticmethod
    def _get_emoji(level: Union[int, str]):
        if level == logging.DEBUG or level == "DEBUG":
            return "🛠️"
        elif level == logging.INFO or level == "INFO":
            return "📚"
        elif level == logging.WARNING or level == "WARNING":
            return "🔥"
        elif level == logging.ERROR or level == "ERROR":
            return "⛔️"
        elif level == logging.CRITICAL or level == "CRITICAL":
            return "❌"
        else:
            return "❓"

    @staticmethod
    def _get_formatter():
        # ==============================
        # {asctime} | {levelname} | {name}
        # ------------------------------
        # {message}
        # ==============================
        border_line = "=" * 50
        sep_line = "-" * 50
        formatter = logging.Formatter(
            f"{border_line}\n"
            f"%(asctime)s | %(levelname)s | %(name)s\n"
            f"{sep_line}\n"
            "%(message)s\n"
            f"{border_line}"
        )
        return formatter

    @staticmethod
    def handle_exception(msg: object):
        "Handle exceptions and return formatted message"
        try:
            if not traceback.format_exc().startswith("NoneType: None"):
                if isinstance(msg, Exception):
                    msg = f"{msg.with_traceback()}"
                else:
                    msg = f"{msg}\n{traceback.format_exc()}"
            return msg
        except TypeError:
            # BaseException: An exception is an object that represents an error
            return msg

    @staticmethod
    def handle_msg(level: int, msg: object):
        "Handle messages and return formatted message"
        caller = inspect.stack()[2].function if inspect.stack()[2].function != "<module>" else "main"
        if level == logging.ERROR or level == logging.CRITICAL:
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

logger = Logger("[Search Engine]", level="INFO")
