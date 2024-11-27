from emoji_logger import Logger

def test_func(logger: Logger):
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

logger = Logger(name="API SERVER", level="DEBUG", is_save=False)
test_func(logger)