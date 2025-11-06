"""测试TextDetection + TextRecognition架构"""
import platform
import psutil
import sys
import os
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 检测CPU信息
cpu_processor = platform.processor()
cpu_info = cpu_processor.lower()
is_intel_cpu = 'intel' in cpu_info

# 获取CPU核心/线程数
physical_cores = psutil.cpu_count(logical=False) or 1
logical_threads = psutil.cpu_count(logical=True) or 1
optimal_threads = max(1, logical_threads // 2)

print("=" * 70)
print("CPU检测结果")
print("=" * 70)
print(f"处理器型号: {cpu_processor}")
print(f"是否Intel CPU: {is_intel_cpu}")
print(f"物理核心数: {physical_cores}")
print(f"逻辑线程数: {logical_threads}")
print(f"推荐线程数: {optimal_threads} (使用一半逻辑线程)")
print(f"MKL-DNN启用: {is_intel_cpu}")
print("=" * 70)

# 测试OCR服务初始化
print("\n开始测试OCR服务初始化（TextDetection + TextRecognition）...")

try:
    from services.ocr_service import OCRService

    print("\n正在初始化OCR服务...")
    ocr_service = OCRService()
    print("✓ OCR服务初始化成功！")
    print("  - 模式: Mobile检测 + 裁剪 + Mobile识别")
    print("  - 检测: PP-OCRv5_mobile_det")
    print("  - 识别: PP-OCRv5_mobile_rec")
    print("  - 策略: 先检测定位，裁剪后识别（提高准确度）")

    # 健康检查
    print("\n正在进行健康检查...")
    is_healthy = ocr_service.health_check()
    if is_healthy:
        print("✓ OCR引擎健康检查通过！")
    else:
        print("✗ OCR引擎健康检查失败！")

    # 测试图片识别
    print("\n测试图片识别...")
    fixtures_dir = Path(__file__).parent / "tests" / "fixtures" / "images"
    test_image = fixtures_dir / "amount_100.jpg"

    if test_image.exists():
        print(f"测试图片: {test_image}")
        with open(test_image, 'rb') as f:
            image_bytes = f.read()

        amount, confidence, time_ms, raw_text, warnings = ocr_service.recognize_amount(
            image_bytes, "amount_100.jpg"
        )

        print(f"\n识别结果:")
        print(f"  金额: {amount}")
        print(f"  置信度: {confidence:.2f}")
        print(f"  处理时间: {time_ms}ms")
        print(f"  原始文本: {raw_text}")
        print(f"  警告: {warnings}")

        # 预期性能：检测(~120ms) + 识别(~30ms) = ~150ms
        if time_ms < 200:
            print(f"\n✓ 性能优秀！ 处理时间 {time_ms}ms < 200ms")
        elif time_ms < 300:
            print(f"\n✓ 性能良好，处理时间 {time_ms}ms < 300ms")
        else:
            print(f"\n⚠ 性能异常，处理时间 {time_ms}ms >= 300ms")
    else:
        print(f"✗ 测试图片不存在: {test_image}")
        print("请先运行: python tests\\fixtures\\generate_test_images.py")

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
