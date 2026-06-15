import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_router import api_router
from app.client.http_client import http_client
from app.core.config import settings
from app.core.exceptions import register_exceptions
from app.core.logger import init_logger
from app.core import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    logger.info(f"{settings.APP_NAME} is starting up...")
    scheduler.start_scheduler()
    yield
    logger.info(f"{settings.APP_NAME} is shutting down...")
    scheduler.stop_scheduler()
    await http_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
        return response

    register_exceptions(app)
    app.include_router(api_router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
