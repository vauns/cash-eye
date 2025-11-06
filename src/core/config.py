"""配置管理模块"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # 日志配置
    LOG_LEVEL: str = "INFO"

    # 文件限制
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024

    # 超时配置
    REQUEST_TIMEOUT_SEC: int = 30
    OCR_TIMEOUT_SEC: int = 3

    # 服务信息
    SERVICE_NAME: str = "money-ocr-api"
    SERVICE_VERSION: str = "1.0.0"

    # 支持的图片格式
    SUPPORTED_FORMATS: list = ["image/jpeg", "image/png", "image/bmp", "image/tiff"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
