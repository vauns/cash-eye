"""图片处理器单元测试"""
import pytest
from PIL import Image
import io

from src.services.image_processor import preprocess_image


def test_preprocess_image_rgb():
    """测试RGB图片预处理"""
    # 创建测试图片
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    # 预处理
    result = preprocess_image(img_bytes)

    assert result.mode == 'RGB'
    assert result.size == (100, 100)


def test_preprocess_image_grayscale():
    """测试灰度图转RGB"""
    # 创建灰度图
    img = Image.new('L', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    # 预处理
    result = preprocess_image(img_bytes)

    assert result.mode == 'RGB'


def test_preprocess_image_large():
    """测试大图压缩"""
    # 创建超大图片
    img = Image.new('RGB', (3000, 3000), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    # 预处理
    result = preprocess_image(img_bytes)

    assert max(result.size) <= 2048


def test_preprocess_image_invalid():
    """测试无效图片"""
    with pytest.raises(ValueError):
        preprocess_image(b"invalid image data")
