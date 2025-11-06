"""验证安装和导入"""
import sys

print("正在验证依赖包安装...")

try:
    import fastapi
    print(f"✓ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"✗ FastAPI 未安装: {e}")
    sys.exit(1)

try:
    import paddleocr
    print(f"✓ PaddleOCR 已安装")
except ImportError as e:
    print(f"✗ PaddleOCR 未安装: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print(f"✓ Pillow 已安装")
except ImportError as e:
    print(f"✗ Pillow 未安装: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"✓ Uvicorn {uvicorn.__version__}")
except ImportError as e:
    print(f"✗ Uvicorn 未安装: {e}")
    sys.exit(1)

try:
    import structlog
    print(f"✓ structlog 已安装")
except ImportError as e:
    print(f"✗ structlog 未安装: {e}")
    sys.exit(1)

try:
    from pydantic import BaseModel
    print(f"✓ Pydantic 已安装")
except ImportError as e:
    print(f"✗ Pydantic 未安装: {e}")
    sys.exit(1)

print("\n正在验证项目模块...")

try:
    from src.core.config import settings
    print(f"✓ 配置模块: {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
except ImportError as e:
    print(f"✗ 配置模块导入失败: {e}")
    sys.exit(1)

try:
    from src.core.logging import get_logger
    print("✓ 日志模块")
except ImportError as e:
    print(f"✗ 日志模块导入失败: {e}")
    sys.exit(1)

try:
    from src.api.schemas import RecognitionResponse
    print("✓ API模型")
except ImportError as e:
    print(f"✗ API模型导入失败: {e}")
    sys.exit(1)

try:
    from src.services.image_processor import preprocess_image
    print("✓ 图片处理服务")
except ImportError as e:
    print(f"✗ 图片处理服务导入失败: {e}")
    sys.exit(1)

try:
    from src.services.ocr_service import get_ocr_service
    print("✓ OCR服务")
except ImportError as e:
    print(f"✗ OCR服务导入失败: {e}")
    sys.exit(1)

print("\n✓ 所有依赖和模块验证通过!")
print("\n启动服务命令:")
print("  python -m uvicorn main:app --host 0.0.0.0 --port 8000")
print("\n或使用Docker:")
print("  docker-compose up --build")
