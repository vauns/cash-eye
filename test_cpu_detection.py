"""测试CPU检测功能"""
import platform
import psutil

# 检测CPU信息
cpu_processor = platform.processor()
cpu_info = cpu_processor.lower()
is_intel_cpu = 'intel' in cpu_info

# 获取CPU核心/线程数
physical_cores = psutil.cpu_count(logical=False) or 1
logical_threads = psutil.cpu_count(logical=True) or 1
optimal_threads = max(1, logical_threads // 2)

print("=" * 60)
print("CPU检测结果")
print("=" * 60)
print(f"处理器型号: {cpu_processor}")
print(f"是否Intel CPU: {is_intel_cpu}")
print(f"物理核心数: {physical_cores}")
print(f"逻辑线程数: {logical_threads}")
print(f"推荐线程数: {optimal_threads} (使用一半逻辑线程)")
print(f"MKL-DNN启用: {is_intel_cpu}")
print("=" * 60)

# 测试OCR服务初始化
print("\n开始测试OCR服务初始化...")
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from services.ocr_service import OCRService

    print("正在初始化OCR服务...")
    ocr_service = OCRService()
    print("✓ OCR服务初始化成功！")

    # 健康检查
    print("\n正在进行健康检查...")
    is_healthy = ocr_service.health_check()
    if is_healthy:
        print("✓ OCR引擎健康检查通过！")
    else:
        print("✗ OCR引擎健康检查失败！")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
