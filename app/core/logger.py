import sys
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """
    将标准 logging 的日志接管到 Loguru
    """
    def emit(self, record):
        # 1. 获取对应的 Loguru 日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 2. 【关键修改】动态计算堆栈深度
        # 这一段代码会不断往上找调用方，直到跳出 logging 库的文件范围
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 3. 发送给 Loguru
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def init_logger():
    """
    初始化 Loguru，并彻底接管标准日志
    """
    # 1. 移除 Loguru 默认的 handler
    logger.remove()

    # 2. 添加 Loguru 的 Console handler
    logger.add(
        sys.stdout,
        level="INFO",
        # format 建议加上，不然看着乱
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        backtrace=False,
        diagnose=False
    )
    # 日志文件配置
    # logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days", level="INFO")

    # 3. 【关键一步】接管 Root Logger (防止重复打印)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 4. 指定要拦截的模块
    loggers_to_intercept = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy",  # ORM 总日志
        "sqlalchemy.engine",  # SQL 语句日志
    ]

    for name in loggers_to_intercept:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]  # 替换 Handler
        logging_logger.propagate = False  # 【关键】禁止向上传递，防止重复

        # 强制设置级别，确保 SQLAlchemy 即使 echo=False 也能输出 SQL
        logging_logger.setLevel(logging.INFO)

    # 解决 uvicorn 重复日志的特殊处理
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


__all__ = ["init_logger", "logger"]