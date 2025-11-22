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
    """Verify that all log types are intercepted and formatted consistently"""
    logger.info("[Loguru] This is a native loguru info.")
    logging.getLogger("test_standard").info("[Standard] This is a standard logging info (Intercepted).")
    session.exec(text("SELECT 1"))
    return {"msg": "Check your console! 4 types of logs should look identical."}
