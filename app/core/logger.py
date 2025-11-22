import sys
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """Intercept standard logging to Loguru"""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Calculate stack depth to show correct caller location
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def init_logger():
    """Initialize Loguru and intercept standard logging"""
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        backtrace=False,
        diagnose=False
    )

    # Intercept root logger to prevent duplicate logs
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    loggers_to_intercept = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy",
        "sqlalchemy.engine",
    ]

    for name in loggers_to_intercept:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
        logging_logger.setLevel(logging.INFO)

    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


__all__ = ["init_logger", "logger"]