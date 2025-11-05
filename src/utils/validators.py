"""输入验证工具"""
from typing import Tuple
from fastapi import UploadFile, HTTPException, status

from src.core.config import settings


def validate_image_format(file: UploadFile) -> None:
    """验证图片格式

    Args:
        file: 上传的文件

    Raises:
        HTTPException: 格式不支持时抛出400错误
    """
    if file.content_type not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "UNSUPPORTED_FORMAT",
                "message": f"不支持的图片格式: {file.content_type}",
                "details": f"支持的格式: {', '.join(settings.SUPPORTED_FORMATS)}"
            }
        )


async def validate_file_size(file: UploadFile) -> bytes:
    """验证文件大小并读取内容

    Args:
        file: 上传的文件

    Returns:
        文件内容(字节)

    Raises:
        HTTPException: 文件过大时抛出413错误
    """
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"文件大小超过{settings.MAX_FILE_SIZE_MB}MB限制",
                "details": f"当前大小: {file_size_mb:.2f}MB"
            }
        )

    return content


async def validate_upload_file(file: UploadFile) -> Tuple[bytes, str]:
    """验证上传文件(格式+大小)

    Args:
        file: 上传的文件

    Returns:
        (文件内容, 文件名)元组

    Raises:
        HTTPException: 验证失败时抛出相应错误
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NO_FILE_PROVIDED",
                "message": "未提供文件"
            }
        )

    validate_image_format(file)
    content = await validate_file_size(file)

    return content, file.filename
