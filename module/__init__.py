import re
from .logger import *

with open("pyproject.toml", "r", encoding="utf-8") as f:
    pyproject = f.read()

__version__ = re.search(r'version = "(.*?)"', pyproject).group(1)
__description__ = re.search(r'description = "(.*?)"', pyproject).group(1)
__author__ = re.search(r"authors = \[(.*?)\]", pyproject).group(1)
__license__ = re.search(r'license = "(.*?)"', pyproject).group(1)
__readme__ = re.search(r'readme = "(.*?)"', pyproject).group(1)
