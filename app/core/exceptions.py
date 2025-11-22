from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import logger
from app.models.response import Response


def register_exceptions(app: FastAPI):
    """Register global exception handlers"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP error: {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content=Response.fail(code=exc.status_code, msg=str(exc.detail)).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_msg = "; ".join([f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()])
        logger.warning(f"validation params: {error_msg} - Path: {request.url.path}")

        return JSONResponse(
            status_code=422,
            content=Response.fail(code=422, msg=f"validation params: {error_msg}").model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"server unknown err: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=Response.fail(code=500, msg="system error").model_dump()
        )
