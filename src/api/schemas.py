"""API数据模型定义"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 错误响应模型 ====================

class ErrorDetail(BaseModel):
    """错误详情"""
    code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[str] = Field(None, description="详细错误描述")


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="请求是否成功")
    error: ErrorDetail = Field(..., description="错误详情")


# ==================== 识别响应模型 ====================

class RecognitionResult(BaseModel):
    """识别结果"""
    amount: Optional[str] = Field(None, description="识别出的金额(纯数字格式)")
    confidence: float = Field(..., description="识别置信度(0-1)")
    processing_time_ms: int = Field(..., description="处理耗时(毫秒)")
    raw_text: Optional[str] = Field(None, description="OCR原始识别文本")
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")


class RecognitionResponse(BaseModel):
    """单张图片识别响应"""
    success: bool = Field(True, description="请求是否成功")
    data: RecognitionResult = Field(..., description="识别结果")


# ==================== 批量识别响应模型 ====================

class BatchItemResult(BaseModel):
    """批量识别单项结果"""
    index: int = Field(..., description="图片索引(从0开始)")
    filename: str = Field(..., description="文件名")
    success: bool = Field(..., description="该项是否成功")
    data: Optional[RecognitionResult] = Field(None, description="识别结果")
    error: Optional[ErrorDetail] = Field(None, description="错误信息")


class BatchRecognitionResult(BaseModel):
    """批量识别结果"""
    total: int = Field(..., description="总图片数")
    succeeded: int = Field(..., description="成功识别数")
    failed: int = Field(..., description="失败数")
    results: List[BatchItemResult] = Field(..., description="各图片识别结果")


class BatchRecognitionResponse(BaseModel):
    """批量识别响应"""
    success: bool = Field(True, description="请求是否成功")
    data: BatchRecognitionResult = Field(..., description="批量识别结果")


# ==================== 健康检查响应模型 ====================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态(healthy/unhealthy)")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    ocr_engine: str = Field(..., description="OCR引擎信息")
    uptime_seconds: int = Field(..., description="服务运行时长(秒)")
