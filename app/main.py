import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from loguru import logger
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import register_exceptions
from app.core.logger import init_logger

from app.api.test_api import router as test_router
from app.models.response import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_logger()
    logger.info(f"{settings.APP_NAME} is starting up...")
    yield
    logger.info(f"{settings.APP_NAME} is shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        description="A minimal but robust FastAPI template."
    )

    # 1. 【必加】配置 CORS (解决跨域问题)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境建议改成具体的前端域名 ["http://localhost:8080"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 【推荐】请求耗时处理中间件
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        # 在响应头里添加耗时，单位毫秒
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
        return response

    # 注册全局异常
    register_exceptions(app)

    # 注册路由
    app.include_router(test_router)

    return app

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

register_exceptions(app)

app.include_router(test_router)

@app.get("/")
async def root():
    return Response.success(data="Welcome to the FastAPI application!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
