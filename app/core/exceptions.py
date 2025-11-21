from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import logger
from app.models.response import Response


def register_exceptions(app: FastAPI):
    """
    注册全局异常处理
    """

    # 1. 处理 FastAPI/Starlette 抛出的 HTTP 异常 (如 404, 403)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP error: {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content=Response.fail(code=exc.status_code, msg=str(exc.detail)).model_dump()
        )

    # 2. 处理参数校验异常 (Pydantic 校验失败)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 拼接详细的错误信息，比如 "username 字段缺失"
        error_msg = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()])
        logger.warning(f"validation params: {error_msg} - Path: {request.url.path}")

        return JSONResponse(
            status_code=422,
            content=Response.fail(code=422, msg=f"validation params: {error_msg}").model_dump()
        )

    # 3. 处理所有未知的服务器内部异常 (500)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"server unknown err: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=Response.fail(code=500, msg="system error").model_dump()
        )
