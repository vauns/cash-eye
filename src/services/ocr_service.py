"""OCR识别服务"""
import re
import time
import signal
import platform
from typing import Optional, Tuple, List
import numpy as np
import psutil
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
            # 检测CPU信息
            cpu_processor = platform.processor()
            cpu_info = cpu_processor.lower()
            is_intel_cpu = 'intel' in cpu_info

            # 获取CPU核心/线程数
            physical_cores = psutil.cpu_count(logical=False) or 1
            logical_threads = psutil.cpu_count(logical=True) or 1
            optimal_threads = max(1, logical_threads // 2)  # 使用一半逻辑线程

            # 详细日志输出
            logger.info(
                "cpu_detection",
                processor=cpu_processor,
                is_intel=is_intel_cpu,
                physical_cores=physical_cores,
                logical_threads=logical_threads,
                optimal_threads=optimal_threads,
                mkldnn_enabled=is_intel_cpu
            )

            # PaddleOCR 3.3.1 配置
            # 混合模型策略：检测用 Mobile（快），识别用 Server（准）
            # 平衡性能和精度，能正确识别货币符号"¥"
            self.ocr_engine = PaddleOCR(
                # 混合模型：检测快速，识别精准
                text_detection_model_name='PP-OCRv5_mobile_det',     # 轻量级检测（~100ms）
                text_recognition_model_name='PP-OCRv5_server_rec',   # 高精度识别（~400ms）

                # 禁用所有方向相关模块（节省时间）
                use_textline_orientation=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,

                # 识别批处理
                text_recognition_batch_size=1,

                # CPU 自适应优化
                enable_mkldnn=is_intel_cpu,         # 仅Intel CPU启用MKL-DNN加速
                cpu_threads=optimal_threads,        # 使用一半逻辑线程避免过载
            )
            logger.info("ocr_engine_initialized", status="success", mode="full_pipeline", model="mobile_det+server_rec")
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
            preprocess_start = time.time()
            img = preprocess_image(image_bytes)
            preprocess_time = int((time.time() - preprocess_start) * 1000)
            logger.debug("step_preprocess", time_ms=preprocess_time, size=img.size)

            # 2. 转换为numpy数组供PaddleOCR使用
            array_start = time.time()
            img_array = np.array(img)
            array_time = int((time.time() - array_start) * 1000)
            logger.debug("step_to_array", time_ms=array_time, shape=img_array.shape)

            # 3. OCR识别（仅识别模式，因为未加载检测模型）
            ocr_start = time.time()
            logger.debug("ocr_recognizing", filename=filename, mode="rec_only")
            result = self.ocr_engine.ocr(img_array)
            ocr_time = int((time.time() - ocr_start) * 1000)
            logger.debug("step_ocr", time_ms=ocr_time)

            # 取消超时
            if timeout_set:
                signal.alarm(0)

            # 4. 提取文本和置信度
            if not result:
                processing_time = int((time.time() - start_time) * 1000)
                logger.warning(
                    "ocr_no_text_detected",
                    filename=filename,
                    processing_time_ms=processing_time
                )
                return None, 0.0, processing_time, None, ["未检测到任何文本"]

            # PaddleOCR 3.3.1 返回格式：[{字典}]
            # 字典包含 'rec_texts' (识别文本列表) 和 'rec_scores' (置信度列表)
            texts = []
            confidences = []

            if isinstance(result, dict):
                # 直接返回字典格式
                rec_texts = result.get('rec_texts', [])
                rec_scores = result.get('rec_scores', [])

                if rec_texts and rec_scores:
                    texts = [str(t) for t in rec_texts]
                    confidences = [float(s) for s in rec_scores]

            elif isinstance(result, list) and len(result) > 0:
                # 列表格式
                first_item = result[0]

                if isinstance(first_item, dict):
                    # PaddleOCR 3.3.1: [{'rec_texts': [...], 'rec_scores': [...], ...}]
                    rec_texts = first_item.get('rec_texts', [])
                    rec_scores = first_item.get('rec_scores', [])

                    if rec_texts and rec_scores:
                        texts = [str(t) for t in rec_texts]
                        confidences = [float(s) for s in rec_scores]
                        logger.debug("ocr_dict_format_parsed",
                                   num_texts=len(texts),
                                   texts=texts[:3])  # 只记录前3个
                    else:
                        logger.warning("ocr_empty_dict_result",
                                     filename=filename,
                                     dict_keys=list(first_item.keys()))

                elif isinstance(first_item, (list, tuple)):
                    # 旧版 PaddleOCR: [[coords, (text, conf)], ...]
                    for line in first_item:
                        try:
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                text_info = line[1]
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text = str(text_info[0])
                                    confidence = float(text_info[1])
                                    texts.append(text)
                                    confidences.append(confidence)
                        except Exception as e:
                            logger.error("error_parsing_line", error=str(e), line=str(line))
                            continue

                else:
                    logger.warning("unexpected_first_item_type",
                                 first_item_type=str(type(first_item)),
                                 filename=filename)

            raw_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # 如果没有提取到任何文本
            if not texts:
                processing_time = int((time.time() - start_time) * 1000)
                logger.warning(
                    "ocr_no_text_extracted",
                    filename=filename,
                    processing_time_ms=processing_time,
                    result_type=str(type(result)),
                    result_len=len(result) if isinstance(result, list) else 0
                )
                return None, 0.0, processing_time, None, ["未检测到任何文本"]

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
            self.ocr_engine.ocr(img_array)
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
