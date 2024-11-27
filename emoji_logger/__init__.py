import sys
import inspect
import logging
import traceback
from typing import Optional, Union
from pathlib import Path


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
    :param level: Union[str, int]: Logging level (default: logging.DEBUG)
    :param is_save: bool: Save log to file (default: False)
    :param log_path: Optional[str]: Path to save log file (default: None)
    """

    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.DEBUG,
        is_save: bool = False,
        log_path: Optional[str] = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_level(level))
        self._set_stream_handler()
        if is_save:
            if not log_path:
                raise ValueError("log_path is required when is_save is True")
            self.log_path = Path(log_path)
            self._set_file_handler(self.log_path)

    def _set_stream_handler(self):
        self.console_handler = logging.StreamHandler(stream=sys.stdout)
        self.console_handler.setFormatter(Logger._get_formatter())
        self.logger.addHandler(self.console_handler)
        self.logger.addFilter(DuplicateFilter())

    def _set_file_handler(self):
        if not self.log_path.parent.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_handler = logging.FileHandler(self.log_path)
        self.file_handler.setFormatter(Logger._get_formatter())
        self.logger.addHandler(self.file_handler)
        self.logger.addFilter(DuplicateFilter())

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
        """
        Formatter to include module, filename, function name, and line number in the logs.
        Dynamically determines the correct call stack frame for accurate line numbers.

        Example:
        ```
        ==================================================
        %(asctime)s | %(levelname)s | %(name)
        %(filename)s | %(funcName)s | %(lineno)d
        --------------------------------------------------
        %(message)s
        ==================================================
        ```
        """
        border_line = "=" * 50
        sep_line = "-" * 50

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                caller_stack = inspect.stack()
                for frame_info in caller_stack:
                    frame = frame_info[0]
                    module = inspect.getmodule(frame)
                    if module:
                        module_name = module.__name__
                        if not module_name.startswith(
                            "emoji_logger"
                        ) and not module_name.startswith("logging"):
                            if len(frame_info.filename.split("/")) > 3:
                                record.filename = '/'.join(frame_info.filename.split("/")[-3:])
                            else:
                                record.filename = frame_info.filename
                            record.funcName = frame_info.function
                            record.lineno = frame_info.lineno
                            break
                return super().format(record)

        formatter = CustomFormatter(
            f"{border_line}\n"
            f"%(asctime)s | %(levelname)s | %(name)s\n"
            f"%(filename)s | %(funcName)s | %(lineno)d\n"
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
        caller = (
            inspect.stack()[2].function
            if inspect.stack()[2].function != "<module>"
            else "main"
        )
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


logger = Logger(name="MAIN", level=logging.INFO, is_save=False)

if __name__ == "__main__":
    print(__file__.split("/")[-1].replace(".py", ""))
