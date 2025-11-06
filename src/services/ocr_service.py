"""OCR识别服务"""
import re
import time
import signal
from typing import Optional, Tuple, List
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

from src.core.config import settings
from src.core.logging import get_logger
from src.services.image_processor import preprocess_image


class TimeoutException(Exception):
    """超时异常"""
    pass


def timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutException("OCR处理超时")

logger = get_logger(__name__)


class OCRService:
    """OCR识别服务类"""

    def __init__(self):
        """初始化PaddleOCR引擎"""
        logger.info("ocr_engine_initializing", engine="PaddleOCR", version="3.3.1")

        try:
            self.ocr_engine = PaddleOCR(
                use_textline_orientation=True,  # 支持旋转图片 (替代use_angle_cls)
                lang='ch',                       # 中文+数字识别
            )
            logger.info("ocr_engine_initialized", status="success")
        except Exception as e:
            logger.error("ocr_engine_init_failed", error=str(e))
            raise

    def recognize_amount(
        self,
        image_bytes: bytes,
        filename: str = "unknown"
    ) -> Tuple[Optional[str], float, int, Optional[str], List[str]]:
        """识别图片中的金额

        Args:
            image_bytes: 图片字节数据
            filename: 文件名(用于日志)

        Returns:
            (金额, 置信度, 处理时间ms, 原始文本, 警告列表)元组

        Raises:
            Exception: OCR处理失败
        """
        start_time = time.time()
        warnings = []

        try:
            # 设置超时(仅在Unix系统上有效,Windows上signal.alarm不可用)
            timeout_set = False
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(settings.OCR_TIMEOUT_SEC)
                timeout_set = True

            # 1. 图片预处理
            img = preprocess_image(image_bytes)

            # 2. 转换为numpy数组供PaddleOCR使用
            img_array = np.array(img)

            # 3. OCR识别
            logger.debug("ocr_recognizing", filename=filename)
            result = self.ocr_engine.ocr(img_array, cls=True)

            # 取消超时
            if timeout_set:
                signal.alarm(0)

            # 4. 提取文本和置信度
            if not result or not result[0]:
                processing_time = int((time.time() - start_time) * 1000)
                logger.warning(
                    "ocr_no_text_detected",
                    filename=filename,
                    processing_time_ms=processing_time
                )
                return None, 0.0, processing_time, None, ["未检测到任何文本"]

            # 提取所有文本和置信度
            texts = []
            confidences = []
            for line in result[0]:
                text = line[1][0]  # 识别的文本
                confidence = line[1][1]  # 置信度
                texts.append(text)
                confidences.append(confidence)

            raw_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # 5. 提取金额
            amount = self._extract_amount_from_text(raw_text)

            # 6. 置信度检查
            if avg_confidence < 0.8:
                warnings.append("置信度较低,建议人工复核")
                logger.warning(
                    "low_confidence_detected",
                    filename=filename,
                    confidence=avg_confidence
                )

            processing_time = int((time.time() - start_time) * 1000)

            logger.info(
                "ocr_completed",
                filename=filename,
                amount=amount,
                confidence=avg_confidence,
                processing_time_ms=processing_time,
                raw_text=raw_text
            )

            return amount, avg_confidence, processing_time, raw_text, warnings

        except TimeoutException as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(
                "ocr_timeout",
                filename=filename,
                processing_time_ms=processing_time,
                timeout_sec=settings.OCR_TIMEOUT_SEC
            )
            raise TimeoutException(f"图片处理超时(>{settings.OCR_TIMEOUT_SEC}秒)")

        except Exception as e:
            # 确保取消超时
            if timeout_set and hasattr(signal, 'SIGALRM'):
                signal.alarm(0)

            processing_time = int((time.time() - start_time) * 1000)
            logger.error(
                "ocr_failed",
                filename=filename,
                error=str(e),
                processing_time_ms=processing_time
            )
            raise

    def _extract_amount_from_text(self, ocr_text: str) -> Optional[str]:
        """从OCR文本中提取金额

        Args:
            ocr_text: OCR识别的文本

        Returns:
            提取的金额字符串(纯数字格式),未找到则返回None
        """
        if not ocr_text:
            return None

        # 清理文本:去除空格、换行
        text = ocr_text.replace(' ', '').replace('\n', '').replace('\r', '')

        # 模式1: 带货币符号的金额 ¥1,234.56 / $1,234.56
        pattern1 = r'[¥$￥]\s*([\d,]+\.?\d*)'

        # 模式2: 纯数字金额 1234.56 / 1,234.56 / 1234
        pattern2 = r'([\d,]+\.?\d+|\d+)'

        # 优先匹配带货币符号
        match = re.search(pattern1, text)
        if match:
            amount = match.group(1)
        else:
            match = re.search(pattern2, text)
            if match:
                amount = match.group(1)
            else:
                logger.debug("no_amount_pattern_matched", text=text)
                return None

        # 标准化:移除千分位逗号
        amount = amount.replace(',', '')

        # 验证:检查是否为合法金额格式
        if re.match(r'^\d+(\.\d{1,2})?$', amount):
            return amount

        logger.debug("invalid_amount_format", extracted=amount)
        return None

    def health_check(self) -> bool:
        """健康检查OCR引擎是否可用

        Returns:
            True表示健康,False表示异常
        """
        try:
            # 尝试识别一个小的测试图片
            test_img = Image.new('RGB', (100, 100), color='white')
            img_array = np.array(test_img)
            self.ocr_engine.ocr(img_array, cls=False)
            return True
        except Exception as e:
            logger.error("ocr_health_check_failed", error=str(e))
            return False


# 全局OCR服务实例(单例模式,避免重复加载模型)
_ocr_service = None


def get_ocr_service() -> OCRService:
    """获取OCR服务实例

    Returns:
        OCRService实例
    """
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
