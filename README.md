# Python Custom Logging Module

This is a custom logging module for Python. It is a simple module that allows you to log messages to a file and/or the console. It also allows you to set the log level so that you can control which messages get logged.

## Installation

1. Automatically install the module using pip:

```bash
pip install emoji_logger
```

2. Manually install the module:
   Way 1. To install the module, simply copy the `logging.py` file to your project directory.

## Usage

Here is an example of how to use the module:

```python
from emoji_logger import Logger # < This is a logger class what you can use to create a logger object
from emoji_logger import logger # < This is a logger object what you can use directly (level: INFO)

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

- Pypi: [emoji_logger](https://pypi.org/project/emoji_logger/)
- GitHub: [Jin-Doh/python-logging](https://github.com/Jin-Doh/python-logging)
