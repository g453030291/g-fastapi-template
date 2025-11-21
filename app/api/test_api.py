import logging

from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session, text

from app.core.database import get_db
from app.models.response import Response

router = APIRouter()

@router.get("/db")
def test_db_connection(session: Session = Depends(get_db)):
    result = session.exec(text("SELECT 1")).first()
    val = result[0] if result else 0
    return Response.success(data=val)


@router.get("/log_check")
def check_logs(session: Session = Depends(get_db)):
    """
    终极日志验证：触发所有类型的日志，检查是否格式统一
    """
    # 1. Loguru 原生日志 (应该显示)
    logger.info("✅ [Loguru] This is a native loguru info.")

    # 2. 标准 Python logging 日志 (应该被拦截并显示，且格式与上面一致)
    logging.getLogger("test_standard").info("✅ [Standard] This is a standard logging info (Intercepted).")

    # 3. SQLAlchemy 引擎日志 (应该被拦截并显示 SQL 语句)
    # 前提：database.py 里 echo=False，且 logger.py 里开启了 sqlalchemy.engine 的 INFO 级别
    session.exec(text("SELECT 1"))

    # 4. 这里的 return 会触发 Uvicorn 的 Access Log (应该被拦截并显示)
    return {"msg": "Check your console! 4 types of logs should look identical."}
