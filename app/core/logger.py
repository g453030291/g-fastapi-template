import sys
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logger():
    logger.remove()

    logger.configure(patcher=lambda record: record["extra"].setdefault("request_id", "-"))

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> | <dim>{extra[request_id]}</dim> - <level>{message}</level>",
        backtrace=False,
        diagnose=False,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "sqlalchemy", "sqlalchemy.engine"]:
        log = logging.getLogger(name)
        log.handlers = [InterceptHandler()]
        log.propagate = False
        log.setLevel(logging.INFO)


__all__ = ["init_logger", "logger"]
