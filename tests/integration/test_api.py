"""Integration tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def fixtures_dir():
    """Get fixtures directory path"""
    return Path(__file__).parent.parent / "fixtures" / "images"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert data["status"] == "healthy"


def test_recognize_endpoint_success(client, fixtures_dir):
    """Test successful image recognition"""
    image_path = fixtures_dir / "amount_100.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "success" in data
    assert "data" in data
    assert data["success"] is True

    # Check data structure
    result = data["data"]
    assert "amount" in result
    assert "confidence" in result
    assert "processing_time_ms" in result
    assert "raw_text" in result
    assert "warnings" in result

    # Validate data types
    assert isinstance(result["confidence"], (int, float))
    assert isinstance(result["processing_time_ms"], (int, float))
    assert isinstance(result["warnings"], list)
    assert result["amount"] is None or isinstance(result["amount"], str)


def test_recognize_endpoint_png(client, fixtures_dir):
    """Test recognition with PNG format"""
    image_path = fixtures_dir / "amount_200.png"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.png", f, "image/png")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_recognize_endpoint_bmp(client, fixtures_dir):
    """Test recognition with BMP format"""
    image_path = fixtures_dir / "amount_300.bmp"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.bmp", f, "image/bmp")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_recognize_endpoint_no_file(client):
    """Test endpoint without file"""
    response = client.post("/api/v1/recognize")

    assert response.status_code == 422  # Unprocessable Entity


def test_recognize_endpoint_invalid_format(client, fixtures_dir):
    """Test endpoint with unsupported format"""
    # Create a fake file with wrong extension
    image_path = fixtures_dir / "amount_100.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.txt", f, "text/plain")}
        )

    # Should reject unsupported format
    assert response.status_code == 400
    data = response.json()
    # FastAPI returns error in 'detail' field
    assert "detail" in data


def test_recognize_endpoint_various_amounts(client, fixtures_dir):
    """Test recognition with various amount formats"""
    test_images = [
        "amount_100.jpg",
        "amount_1234.jpg",
        "amount_dollar_99.jpg",
        "amount_yuan_888.jpg",
        "amount_50.jpg",
    ]

    for image_name in test_images:
        image_path = fixtures_dir / image_name

        if not image_path.exists():
            pytest.skip(f"Test image not found: {image_path}")

        with open(image_path, "rb") as f:
            response = client.post(
                "/api/v1/recognize",
                files={"file": (image_name, f, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # If amount is extracted, it should be numeric (with optional decimal point and comma)
        if data["data"]["amount"]:
            amount = data["data"]["amount"]
            assert amount.replace('.', '').replace(',', '').isdigit()


def test_batch_recognize_endpoint_success(client, fixtures_dir):
    """Test batch recognition with multiple images"""
    image_paths = [
        fixtures_dir / "amount_100.jpg",
        fixtures_dir / "amount_200.png",
    ]

    files = []
    for path in image_paths:
        files.append(("files", (path.name, open(path, "rb"), "image/jpeg")))

    try:
        response = client.post("/api/v1/recognize/batch", files=files)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

        # Check batch data structure
        batch_data = data["data"]
        assert "total" in batch_data
        assert "succeeded" in batch_data
        assert "failed" in batch_data
        assert "results" in batch_data

        # Verify counts
        assert batch_data["total"] == 2
        assert isinstance(batch_data["results"], list)
        assert len(batch_data["results"]) == 2

    finally:
        # Close all opened files
        for _, file_tuple in files:
            file_tuple[1].close()


def test_batch_recognize_single_file(client, fixtures_dir):
    """Test batch recognition with single image"""
    image_path = fixtures_dir / "amount_100.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize/batch",
            files=[("files", (image_path.name, f, "image/jpeg"))]
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 1


def test_batch_recognize_empty(client):
    """Test batch recognition with no files"""
    response = client.post("/api/v1/recognize/batch", files=[])

    # Should handle empty batch
    assert response.status_code in [200, 400, 422]


def test_recognize_endpoint_low_confidence(client, fixtures_dir):
    """Test recognition with low confidence image"""
    image_path = fixtures_dir / "amount_blurry.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("blurry.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Low quality images might have warnings
    if data["data"]["confidence"] < 0.8:
        assert len(data["data"]["warnings"]) > 0


def test_recognize_endpoint_no_text(client, fixtures_dir):
    """Test recognition with image containing no text"""
    image_path = fixtures_dir / "no_text.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("empty.jpg", f, "image/jpeg")}
        )

    # Should handle gracefully
    assert response.status_code == 200
    data = response.json()
    # May or may not extract amount - both are acceptable


def test_api_cors_headers(client):
    """Test that API returns appropriate headers"""
    response = client.get("/api/v1/health")

    # Should have content type
    assert "content-type" in response.headers
    assert "application/json" in response.headers["content-type"]


def test_recognize_endpoint_response_time(client, fixtures_dir):
    """Test that API responds within reasonable time"""
    image_path = fixtures_dir / "amount_100.jpg"

    import time
    start = time.time()

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )

    elapsed = time.time() - start

    assert response.status_code == 200

    # Should respond within 10 seconds
    # (generous to account for model loading on first run)
    assert elapsed < 10, f"API took too long: {elapsed:.2f}s"


def test_recognize_endpoint_confidence_range(client, fixtures_dir):
    """Test that confidence values are in valid range"""
    image_path = fixtures_dir / "amount_100.jpg"

    with open(image_path, "rb") as f:
        response = client.post(
            "/api/v1/recognize",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 200
    data = response.json()

    confidence = data["data"]["confidence"]
    assert 0 <= confidence <= 1, f"Confidence {confidence} is out of range [0,1]"
