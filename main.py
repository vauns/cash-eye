"""应用入口文件"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.api import routes

# 配置日志
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(
        "service_starting",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        port=settings.PORT
    )
    yield
    # 关闭时
    logger.info("service_stopping")


# 创建FastAPI应用
app = FastAPI(
    title="金额识别OCR服务",
    description="基于PaddleOCR v3.3.1 (PP-OCRv5)的金额识别API服务,支持单张和批量图片识别",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(routes.router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running"
    }
