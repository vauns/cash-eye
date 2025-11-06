"""Unit tests for OCR service"""
import pytest
from pathlib import Path
from PIL import Image
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.ocr_service import OCRService


@pytest.fixture
def ocr_service():
    """Create OCR service instance"""
    return OCRService()


@pytest.fixture
def fixtures_dir():
    """Get fixtures directory path"""
    return Path(__file__).parent.parent / "fixtures" / "images"


def test_ocr_service_initialization(ocr_service):
    """Test OCR service can be initialized"""
    assert ocr_service is not None
    assert hasattr(ocr_service, 'recognize_amount')


def test_recognize_amount_basic(ocr_service, fixtures_dir):
    """Test basic amount recognition"""
    image_path = str(fixtures_dir / "amount_100.jpg")

    # Check that image exists
    assert os.path.exists(image_path), f"Test image not found: {image_path}"

    # Read image as bytes
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_100.jpg")

    # Basic validation
    assert time_ms > 0, "Processing time should be positive"
    assert 0 <= confidence <= 1, "Confidence should be between 0 and 1"
    assert raw_text is not None, "Raw text should not be None"

    # Amount validation
    if amount:
        assert amount.replace('.', '').replace(',', '').isdigit(), "Amount should be numeric"


def test_recognize_amount_with_currency_symbol(ocr_service, fixtures_dir):
    """Test amount recognition with currency symbol"""
    image_path = str(fixtures_dir / "amount_yuan_888.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_yuan_888.jpg")

    assert time_ms > 0
    assert 0 <= confidence <= 1

    # If amount is extracted, it should not contain currency symbols
    if amount:
        assert '¥' not in amount
        assert '$' not in amount
        assert '￥' not in amount


def test_recognize_amount_with_comma(ocr_service, fixtures_dir):
    """Test amount recognition with thousand separator"""
    image_path = str(fixtures_dir / "amount_comma_1234.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_comma_1234.jpg")

    assert time_ms > 0
    assert 0 <= confidence <= 1

    # Amount can contain comma or have it removed
    if amount:
        # Should be a valid number format
        assert amount.replace(',', '').replace('.', '').isdigit()


def test_recognize_amount_different_formats(ocr_service, fixtures_dir):
    """Test OCR works with different image formats"""
    test_images = [
        "amount_100.jpg",
        "amount_200.png",
        "amount_300.bmp",
    ]

    for image_name in test_images:
        image_path = str(fixtures_dir / image_name)

        if not os.path.exists(image_path):
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, image_name)

        # Should complete without errors
        assert time_ms > 0
        assert 0 <= confidence <= 1


def test_recognize_amount_low_quality(ocr_service, fixtures_dir):
    """Test OCR with low quality/blurry image"""
    image_path = str(fixtures_dir / "amount_blurry.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_blurry.jpg")

    # Should complete even with low quality
    assert time_ms > 0
    assert 0 <= confidence <= 1

    # Low quality might trigger warnings
    if confidence < 0.8:
        assert len(warnings) > 0, "Should have warnings for low confidence"


def test_recognize_amount_no_text(ocr_service, fixtures_dir):
    """Test OCR with image containing no text"""
    image_path = str(fixtures_dir / "no_text.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "no_text.jpg")

    # Should complete without errors
    assert time_ms > 0
    assert 0 <= confidence <= 1

    # Might not extract amount from blank image
    # This is acceptable behavior


def test_recognize_amount_invalid_path(ocr_service):
    """Test OCR with invalid file path"""
    with pytest.raises(Exception):
        # Pass invalid bytes data
        ocr_service.recognize_amount(b"invalid image data", "invalid.jpg")


def test_recognize_amount_returns_tuple(ocr_service, fixtures_dir):
    """Test that recognize_amount returns correct tuple structure"""
    image_path = str(fixtures_dir / "amount_100.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    result = ocr_service.recognize_amount(image_bytes, "amount_100.jpg")

    # Should return a tuple with 5 elements
    assert isinstance(result, tuple), "Result should be a tuple"
    assert len(result) == 5, "Result should have 5 elements"

    amount, confidence, time_ms, raw_text, warnings = result

    # Type checks
    assert amount is None or isinstance(amount, str), "Amount should be string or None"
    assert isinstance(confidence, (int, float)), "Confidence should be numeric"
    assert isinstance(time_ms, (int, float)), "Time should be numeric"
    assert raw_text is None or isinstance(raw_text, str), "Raw text should be string or None"
    assert isinstance(warnings, list), "Warnings should be a list"


def test_recognize_amount_decimal_places(ocr_service, fixtures_dir):
    """Test OCR correctly handles decimal places"""
    image_path = str(fixtures_dir / "amount_0_01.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_0_01.jpg")

    assert time_ms > 0

    # If amount is found, check it has proper decimal format
    if amount and '.' in amount:
        parts = amount.split('.')
        assert len(parts) == 2, "Should have exactly one decimal point"
        assert parts[0].replace(',', '').isdigit(), "Integer part should be numeric"
        assert parts[1].isdigit(), "Decimal part should be numeric"


def test_recognize_amount_large_number(ocr_service, fixtures_dir):
    """Test OCR with large amount"""
    image_path = str(fixtures_dir / "amount_large.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_large.jpg")

    assert time_ms > 0
    assert 0 <= confidence <= 1

    # Should handle large numbers
    if amount:
        clean_amount = amount.replace(',', '').replace('.', '')
        assert clean_amount.isdigit(), "Large amount should still be numeric"


def test_recognize_amount_performance(ocr_service, fixtures_dir):
    """Test that OCR completes within reasonable time"""
    image_path = str(fixtures_dir / "amount_100.jpg")

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(image_bytes, "amount_100.jpg")

    # Should complete within 1 second (1000ms)
    # PaddleOCR 3.3.1 with Mobile det (~100ms) + Server rec (~400ms) + CPU optimization
    # Hybrid model for balance of speed and accuracy
    assert time_ms < 1000, f"OCR took too long: {time_ms}ms"
