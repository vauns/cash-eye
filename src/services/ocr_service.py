"""OCR识别服务"""
import re
import time
import signal
import platform
from typing import Optional, Tuple, List
import numpy as np
import psutil
from PIL import Image
from paddleocr import TextDetection, TextRecognition

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

            # PaddleOCR 3.3.1：Mobile检测+裁剪+Mobile识别
            # 使用检测定位文本区域，裁剪后识别以提高准确度

            # 初始化文本检测引擎
            self.text_detector = TextDetection(
                model_name='PP-OCRv5_mobile_det',   # 轻量级检测（~120ms）
                enable_mkldnn=is_intel_cpu,         # CPU自适应优化
                cpu_threads=optimal_threads,
            )
            logger.info("text_detector_initialized", status="success", model="PP-OCRv5_mobile_det")

            # 初始化文本识别引擎
            self.text_recognizer = TextRecognition(
                model_name='PP-OCRv5_mobile_rec',   # 轻量级识别（~30ms）
                enable_mkldnn=is_intel_cpu,         # CPU自适应优化
                cpu_threads=optimal_threads,
            )
            logger.info("text_recognizer_initialized", status="success", model="PP-OCRv5_mobile_rec")
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

            # 3. 文本检测
            det_start = time.time()
            logger.debug("text_detecting", filename=filename)
            det_result = self.text_detector.predict(input=img_array)
            det_time = int((time.time() - det_start) * 1000)
            logger.debug("step_detection", time_ms=det_time)

            # 调试：查看检测结果格式
            logger.debug("det_result_type", result_type=str(type(det_result)))
            if hasattr(det_result, '__len__'):
                logger.debug("det_result_len", length=len(det_result))

            # 4. 提取检测框并裁剪图片
            crop_start = time.time()
            cropped_images = []

            if isinstance(det_result, list) and len(det_result) > 0:
                first_det = det_result[0]

                # 从字典中获取dt_polys（检测到的多边形坐标）
                if isinstance(first_det, dict) and 'dt_polys' in first_det:
                    dt_polys = first_det['dt_polys']
                    logger.debug("processing_polys", num_polys=len(dt_polys))

                    # 对每个检测到的文本框
                    for idx, poly in enumerate(dt_polys):
                        # poly是多边形顶点坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                        # 转换为bbox (x_min, y_min, x_max, y_max)
                        poly_array = np.array(poly)
                        x_min = int(poly_array[:, 0].min())
                        y_min = int(poly_array[:, 1].min())
                        x_max = int(poly_array[:, 0].max())
                        y_max = int(poly_array[:, 1].max())

                        logger.debug(f"poly_{idx}_bbox", x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)

                        # 添加padding（可选，避免裁剪太紧）
                        padding = 2
                        x_min = max(0, x_min - padding)
                        y_min = max(0, y_min - padding)
                        x_max = min(img.width, x_max + padding)
                        y_max = min(img.height, y_max + padding)

                        # 裁剪图片
                        cropped = img.crop((x_min, y_min, x_max, y_max))
                        cropped_array = np.array(cropped)
                        cropped_images.append(cropped_array)

                        logger.debug(f"cropped_{idx}", size=(x_max-x_min, y_max-y_min), shape=cropped_array.shape)

            crop_time = int((time.time() - crop_start) * 1000)
            logger.debug("step_crop", time_ms=crop_time, num_crops=len(cropped_images))

            # 5. 文本识别（识别裁剪后的图片）
            rec_start = time.time()

            if len(cropped_images) > 0:
                logger.debug("text_recognizing", filename=filename, mode="cropped_images", num_images=len(cropped_images))
                # 批量识别裁剪后的图片
                rec_result = self.text_recognizer.predict(input=cropped_images, batch_size=len(cropped_images))
            else:
                # 如果没有检测到文本框，回退到识别整张图
                logger.warning("no_text_boxes_detected", filename=filename, fallback="full_image")
                rec_result = self.text_recognizer.predict(input=img_array, batch_size=1)

            rec_time = int((time.time() - rec_start) * 1000)
            logger.debug("step_recognition", time_ms=rec_time)

            total_time = det_time + rec_time
            logger.debug("total_det_rec_time", time_ms=total_time)

            # 取消超时
            if timeout_set:
                signal.alarm(0)

            # 5. 解析识别结果
            texts = []
            confidences = []

            # TextRecognition 3.3.1 返回格式解析
            logger.debug("rec_result_type", result_type=str(type(rec_result)), result_len=len(rec_result) if hasattr(rec_result, '__len__') else 'N/A')

            # 详细日志：打印结果内容以便调试
            if isinstance(rec_result, list) and len(rec_result) > 0:
                logger.debug("rec_result_sample", first_item_type=str(type(rec_result[0])), first_item=str(rec_result[0])[:200])

            # 尝试解析结果
            if rec_result is None or (isinstance(rec_result, list) and len(rec_result) == 0):
                processing_time = int((time.time() - start_time) * 1000)
                logger.warning(
                    "no_text_detected",
                    filename=filename,
                    processing_time_ms=processing_time
                )
                return None, 0.0, processing_time, None, ["未检测到任何文本"]

            try:
                # 尝试迭代结果对象
                for idx, res in enumerate(rec_result):
                    logger.debug(f"parsing_rec_item_{idx}", res_type=str(type(res)), has_text=hasattr(res, 'text'), has_score=hasattr(res, 'score'))

                    # 检查是否有text和score属性
                    if hasattr(res, 'text') and hasattr(res, 'score'):
                        texts.append(str(res.text))
                        confidences.append(float(res.score))
                    # 或者是字典格式
                    elif isinstance(res, dict):
                        logger.debug(f"dict_keys_{idx}", keys=list(res.keys()))
                        # PaddleOCR 3.3.1 TextRecognition 返回格式
                        if 'rec_text' in res and 'rec_score' in res:
                            texts.append(str(res['rec_text']))
                            confidences.append(float(res['rec_score']))
                        # 兼容其他可能的格式
                        elif 'text' in res and 'score' in res:
                            texts.append(str(res['text']))
                            confidences.append(float(res['score']))
                    # 或者是元组/列表格式 (text, score)
                    elif isinstance(res, (list, tuple)) and len(res) >= 2:
                        texts.append(str(res[0]))
                        confidences.append(float(res[1]))
                    else:
                        logger.warning("unexpected_rec_result_format", res_type=str(type(res)), res_str=str(res)[:100])

                logger.debug("parsed_recognition_results", num_texts=len(texts), texts=texts[:3])

            except Exception as e:
                logger.error("error_parsing_rec_result", error=str(e), result_type=str(type(rec_result)))

            raw_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # 如果没有提取到任何文本
            if not texts:
                processing_time = int((time.time() - start_time) * 1000)
                logger.warning(
                    "no_text_extracted",
                    filename=filename,
                    processing_time_ms=processing_time
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

        # 验证:检查是否为合法金额格式（标准金额最多2位小数）
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
            # 尝试检测和识别一个小的测试图片
            test_img = Image.new('RGB', (100, 100), color='white')
            img_array = np.array(test_img)

            # 测试检测引擎
            self.text_detector.predict(input=img_array)

            # 测试识别引擎
            self.text_recognizer.predict(input=img_array, batch_size=1)

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
