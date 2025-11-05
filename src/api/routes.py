"""API路由定义"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from src.api.schemas import (
    RecognitionResponse,
    RecognitionResult,
    BatchRecognitionResponse,
    BatchRecognitionResult,
    BatchItemResult,
    HealthCheckResponse,
    ErrorDetail,
)
from src.core.config import settings
from src.core.logging import get_logger
from src.core.uptime import get_uptime
from src.services.ocr_service import get_ocr_service
from src.utils.validators import validate_upload_file

logger = get_logger(__name__)
router = APIRouter()


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize(file: UploadFile = File(...)):
    """单张图片金额识别

    Args:
        file: 上传的图片文件

    Returns:
        识别结果

    Raises:
        HTTPException: 验证失败或识别失败时抛出
    """
    try:
        # 1. 验证文件
        content, filename = await validate_upload_file(file)

        # 2. 获取OCR服务
        ocr_service = get_ocr_service()

        # 3. 识别金额
        amount, confidence, processing_time, raw_text, warnings = ocr_service.recognize_amount(
            content, filename
        )

        # 4. 构造响应
        return RecognitionResponse(
            success=True,
            data=RecognitionResult(
                amount=amount,
                confidence=confidence,
                processing_time_ms=processing_time,
                raw_text=raw_text,
                warnings=warnings
            )
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error("invalid_image", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_IMAGE",
                "message": "图片无效或已损坏",
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error("ocr_engine_error", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "OCR_ENGINE_ERROR",
                "message": "OCR引擎处理失败",
                "details": str(e)
            }
        )


@router.post("/recognize/batch", response_model=BatchRecognitionResponse)
async def recognize_batch(files: List[UploadFile] = File(...)):
    """批量图片金额识别

    Args:
        files: 上传的图片文件列表

    Returns:
        批量识别结果
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NO_FILE_PROVIDED",
                "message": "未提供文件"
            }
        )

    ocr_service = get_ocr_service()
    results = []
    succeeded = 0
    failed = 0

    for index, file in enumerate(files):
        try:
            # 验证并识别
            content, filename = await validate_upload_file(file)
            amount, confidence, processing_time, raw_text, warnings = ocr_service.recognize_amount(
                content, filename
            )

            results.append(BatchItemResult(
                index=index,
                filename=filename,
                success=True,
                data=RecognitionResult(
                    amount=amount,
                    confidence=confidence,
                    processing_time_ms=processing_time,
                    raw_text=raw_text,
                    warnings=warnings
                ),
                error=None
            ))
            succeeded += 1

        except HTTPException as e:
            # HTTP异常(验证失败)
            error_detail = e.detail if isinstance(e.detail, dict) else {"code": "UNKNOWN", "message": str(e.detail)}
            results.append(BatchItemResult(
                index=index,
                filename=file.filename,
                success=False,
                data=None,
                error=ErrorDetail(**error_detail)
            ))
            failed += 1
            logger.warning("batch_item_validation_failed", index=index, filename=file.filename, error=error_detail)

        except Exception as e:
            # 其他异常(识别失败)
            results.append(BatchItemResult(
                index=index,
                filename=file.filename,
                success=False,
                data=None,
                error=ErrorDetail(
                    code="OCR_ENGINE_ERROR",
                    message="OCR引擎处理失败",
                    details=str(e)
                )
            ))
            failed += 1
            logger.error("batch_item_ocr_failed", index=index, filename=file.filename, error=str(e))

    logger.info(
        "batch_recognition_completed",
        total=len(files),
        succeeded=succeeded,
        failed=failed
    )

    return BatchRecognitionResponse(
        success=True,
        data=BatchRecognitionResult(
            total=len(files),
            succeeded=succeeded,
            failed=failed,
            results=results
        )
    )


@router.get("/health", response_model=HealthCheckResponse)
async def health():
    """健康检查

    Returns:
        服务健康状态
    """
    try:
        # 检查OCR引擎是否可用
        ocr_service = get_ocr_service()
        is_healthy = ocr_service.health_check()

        if is_healthy:
            return HealthCheckResponse(
                status="healthy",
                service=settings.SERVICE_NAME,
                version=settings.SERVICE_VERSION,
                ocr_engine="paddleocr-3.3.1",
                uptime_seconds=get_uptime()
            )
        else:
            return HealthCheckResponse(
                status="unhealthy",
                service=settings.SERVICE_NAME,
                version=settings.SERVICE_VERSION,
                ocr_engine="paddleocr-3.3.1",
                uptime_seconds=get_uptime()
            )

    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return HealthCheckResponse(
            status="unhealthy",
            service=settings.SERVICE_NAME,
            version=settings.SERVICE_VERSION,
            ocr_engine="paddleocr-3.3.1",
            uptime_seconds=get_uptime()
        )
