import logging

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.response import Response

router = APIRouter()


@router.get("/db")
async def test_db_connection(session: AsyncSession = Depends(get_db)):
    result = await session.execute(text("SELECT 1"))
    val = result.scalar()
    return Response.success(data=val)


@router.get("/log_check")
async def check_logs(session: AsyncSession = Depends(get_db)):
    """Verify that all log types are intercepted and formatted consistently"""
    logger.info("[Loguru] This is a native loguru info.")
    logging.getLogger("test_standard").info("[Standard] This is a standard logging info (Intercepted).")
    await session.execute(text("SELECT 1"))
    return {"msg": "Check your console! All log types should look identical."}
