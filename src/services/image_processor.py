"""图片预处理服务"""
import io
from PIL import Image

from src.core.logging import get_logger

logger = get_logger(__name__)


def preprocess_image(image_bytes: bytes) -> Image.Image:
    """图片预处理优化识别

    Args:
        image_bytes: 图片字节数据

    Returns:
        预处理后的PIL Image对象

    Raises:
        ValueError: 图片无法打开或处理失败
    """
    try:
        # 打开图片
        img = Image.open(io.BytesIO(image_bytes))

        # 1. 格式转换(统一为RGB)
        if img.mode != 'RGB':
            logger.debug("image_convert", original_mode=img.mode, target_mode="RGB")
            img = img.convert('RGB')

        # 2. 尺寸优化(大图压缩,节省内存和处理时间)
        max_dimension = 2048
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            logger.debug(
                "image_resize",
                original_size=img.size,
                new_size=new_size,
                ratio=ratio
            )
            img = img.resize(new_size, Image.LANCZOS)

        logger.debug(
            "image_preprocessed",
            size=img.size,
            mode=img.mode,
            format=img.format
        )

        return img

    except Exception as e:
        logger.error("image_preprocess_failed", error=str(e))
        raise ValueError(f"图片预处理失败: {str(e)}")
