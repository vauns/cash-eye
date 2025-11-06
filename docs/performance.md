# 性能优化指南

本文档提供 Cash Eye 服务的性能优化建议和最佳实践。

## 目录

- [性能基准](#性能基准)
- [图片优化](#图片优化)
- [并发控制](#并发控制)
- [超时和重试](#超时和重试)
- [资源配置](#资源配置)
- [缓存策略](#缓存策略)
- [监控和分析](#监控和分析)

## 性能基准

### 标准性能指标

| 指标 | 预期值 | 说明 |
|-----|-------|------|
| 单次 OCR 识别 | 1-3秒 | 取决于图片大小和质量 |
| API 响应时间 | < 5秒 | 不包括首次模型加载 |
| 首次启动时间 | 10-30秒 | 包括模型加载 |
| 内存使用 | 1-2GB | 稳定运行状态 |
| CPU 使用 | 30-50% | 单请求处理时 |
| 并发处理能力 | 5-10个请求 | 单实例推荐上限 |

### 影响性能的因素

1. **图片大小**: 大图片处理时间更长
2. **图片质量**: 低质量图片需要更多处理
3. **并发数**: 过多并发导致资源竞争
4. **硬件配置**: CPU 和内存直接影响性能
5. **网络延迟**: 上传和下载时间

## 图片优化

### 推荐图片规格

```python
# 推荐配置
MAX_WIDTH = 2048      # 最大宽度(像素)
MAX_HEIGHT = 2048     # 最大高度(像素)
MAX_FILE_SIZE = 1     # 最大文件大小(MB)
QUALITY = 85          # JPEG 质量(1-100)
FORMAT = "JPEG"       # 推荐格式
```

### 图片预处理脚本

```python
from PIL import Image
import os

def optimize_image(input_path, output_path=None, max_size=2048):
    """
    优化图片以提升识别速度和准确率

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径(默认覆盖原图)
        max_size: 最大尺寸(像素)
    """
    output_path = output_path or input_path

    # 打开图片
    img = Image.open(input_path)

    # 转换为 RGB 模式
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    # 调整尺寸
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 保存为 JPEG
    img.save(output_path, 'JPEG', quality=85, optimize=True)

    # 打印优化结果
    original_size = os.path.getsize(input_path) / 1024 / 1024
    optimized_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"原始大小: {original_size:.2f}MB")
    print(f"优化后: {optimized_size:.2f}MB")
    print(f"压缩率: {(1 - optimized_size/original_size)*100:.1f}%")

# 使用示例
optimize_image("large_invoice.jpg", "optimized_invoice.jpg")
```

### 批量优化

```python
import glob
from pathlib import Path

def batch_optimize(input_dir, output_dir=None, max_size=2048):
    """批量优化图片"""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir else input_dir
    output_dir.mkdir(exist_ok=True)

    # 支持的格式
    patterns = ['*.jpg', '*.jpeg', '*.png', '*.bmp']

    for pattern in patterns:
        for img_path in input_dir.glob(pattern):
            output_path = output_dir / f"opt_{img_path.name}"
            try:
                optimize_image(str(img_path), str(output_path), max_size)
                print(f"✓ {img_path.name}")
            except Exception as e:
                print(f"✗ {img_path.name}: {e}")

# 使用
batch_optimize("./invoices", "./optimized_invoices")
```

### 图片裁剪

只保留金额区域可显著提升准确率和速度：

```python
def crop_amount_region(image_path, bbox):
    """
    裁剪图片只保留金额区域

    Args:
        image_path: 图片路径
        bbox: 边界框 (x1, y1, x2, y2)
    """
    img = Image.open(image_path)
    cropped = img.crop(bbox)
    return cropped

# 使用示例
# 假设金额在图片右下角 500x200 区域
img = Image.open("invoice.jpg")
width, height = img.size
bbox = (width-500, height-200, width, height)
cropped = crop_amount_region("invoice.jpg", bbox)
cropped.save("amount_only.jpg")
```

## 并发控制

### 推荐并发配置

| 场景 | 推荐并发数 | 说明 |
|-----|-----------|------|
| 单实例 | 5-10 | 默认配置 |
| 高性能服务器 | 10-20 | 4核8GB以上 |
| 低配置服务器 | 2-5 | 2核4GB |
| 批量处理 | 3-5 | 使用批量接口更优 |

### Python 并发控制

```python
from concurrent.futures import ThreadPoolExecutor
import requests

class OCRClient:
    def __init__(self, base_url, max_workers=5):
        self.base_url = base_url
        self.max_workers = max_workers

    def recognize_single(self, image_path):
        """识别单张图片"""
        url = f"{self.base_url}/api/v1/recognize"
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, timeout=10)
        return response.json()

    def recognize_concurrent(self, image_paths):
        """并发识别多张图片"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.recognize_single, image_paths))
        return results

# 使用
client = OCRClient("http://localhost:8000", max_workers=5)
images = ["img1.jpg", "img2.jpg", "img3.jpg"]
results = client.recognize_concurrent(images)
```

### 限速器

```python
import time
from threading import Lock

class RateLimiter:
    """简单的限速器"""
    def __init__(self, max_calls, time_window):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()

    def acquire(self):
        """获取许可"""
        with self.lock:
            now = time.time()
            # 清理过期记录
            self.calls = [t for t in self.calls if now - t < self.time_window]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    self.calls = []

            self.calls.append(time.time())

# 使用：限制为每秒最多 10 个请求
limiter = RateLimiter(max_calls=10, time_window=1.0)

def rate_limited_recognize(image_path):
    limiter.acquire()
    return recognize_amount(image_path)
```

## 超时和重试

### 推荐超时配置

```python
TIMEOUT_CONFIG = {
    "connect": 5,      # 连接超时(秒)
    "read": 10,        # 读取超时(秒)
    "single": 10,      # 单张图片总超时
    "batch": 30,       # 批量请求总超时
}
```

### 带重试的客户端

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retries(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504)
):
    """创建带重试机制的 Session"""
    session = requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

# 使用
session = create_session_with_retries()
response = session.post(
    "http://localhost:8000/api/v1/recognize",
    files={"file": open("invoice.jpg", "rb")},
    timeout=(5, 10)  # (connect_timeout, read_timeout)
)
```

### 指数退避重试

```python
import time

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    使用指数退避的重试装饰器

    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        base_delay: 基础延迟(秒)
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            delay = base_delay * (2 ** attempt)
            print(f"重试 {attempt + 1}/{max_retries}，等待 {delay}秒...")
            time.sleep(delay)

# 使用
def recognize():
    return requests.post(url, files=files, timeout=10)

result = retry_with_backoff(recognize, max_retries=3, base_delay=1)
```

## 资源配置

### Docker 资源限制

```bash
# 推荐配置
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  --memory="2g" \
  --memory-swap="2g" \
  --cpus="2.0" \
  --restart unless-stopped \
  money-ocr-api:1.0.0
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  money-ocr:
    image: money-ocr-api:1.0.0
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Kubernetes 资源配置

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### 环境变量优化

```bash
# 性能相关环境变量
LOG_LEVEL=WARNING          # 减少日志输出
MAX_FILE_SIZE_MB=5         # 限制文件大小
OCR_TIMEOUT_SEC=5          # OCR 超时
REQUEST_TIMEOUT_SEC=30     # 请求总超时
```

## 缓存策略

### Redis 缓存示例

```python
import redis
import hashlib
import json

class OCRCache:
    """OCR 结果缓存"""
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = 3600  # 缓存1小时

    def get_cache_key(self, image_path):
        """生成缓存键"""
        with open(image_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"ocr:result:{file_hash}"

    def get(self, image_path):
        """获取缓存"""
        key = self.get_cache_key(image_path)
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, image_path, result):
        """设置缓存"""
        key = self.get_cache_key(image_path)
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(result)
        )

    def recognize_with_cache(self, image_path):
        """带缓存的识别"""
        # 尝试从缓存获取
        cached = self.get(image_path)
        if cached:
            print("从缓存获取")
            return cached

        # 执行识别
        result = recognize_amount(image_path)

        # 缓存结果
        self.set(image_path, result)

        return result
```

### 本地文件缓存

```python
import pickle
from pathlib import Path

class FileCache:
    """基于文件的简单缓存"""
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_path(self, image_path):
        """获取缓存文件路径"""
        file_hash = hashlib.md5(Path(image_path).read_bytes()).hexdigest()
        return self.cache_dir / f"{file_hash}.pkl"

    def get(self, image_path):
        """获取缓存"""
        cache_path = self.get_cache_path(image_path)
        if cache_path.exists():
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        return None

    def set(self, image_path, result):
        """设置缓存"""
        cache_path = self.get_cache_path(image_path)
        with open(cache_path, "wb") as f:
            pickle.dump(result, f)
```

## 监控和分析

### 性能监控

```python
import time
import structlog

logger = structlog.get_logger()

def monitor_performance(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start_time) * 1000

            logger.info(
                "performance_metric",
                function=func.__name__,
                elapsed_ms=elapsed,
                status="success"
            )

            return result
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(
                "performance_metric",
                function=func.__name__,
                elapsed_ms=elapsed,
                status="error",
                error=str(e)
            )
            raise

    return wrapper

# 使用
@monitor_performance
def recognize_amount(image_path):
    # ... 识别逻辑
    pass
```

### 资源监控脚本

```bash
#!/bin/bash
# monitor.sh - 监控 Docker 容器资源使用

while true; do
    echo "=== $(date) ==="
    docker stats money-ocr --no-stream --format \
        "CPU: {{.CPUPerc}} | Memory: {{.MemUsage}} | Net I/O: {{.NetIO}}"
    echo
    sleep 5
done
```

### Prometheus 指标

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
ocr_requests_total = Counter(
    'ocr_requests_total',
    'Total OCR requests',
    ['status']
)

ocr_duration_seconds = Histogram(
    'ocr_duration_seconds',
    'OCR processing duration'
)

ocr_confidence = Gauge(
    'ocr_confidence',
    'OCR result confidence'
)

def recognize_with_metrics(image_path):
    """带指标的识别"""
    start_time = time.time()

    try:
        result = recognize_amount(image_path)

        # 记录指标
        ocr_requests_total.labels(status='success').inc()
        ocr_duration_seconds.observe(time.time() - start_time)
        ocr_confidence.set(result['confidence'])

        return result
    except Exception as e:
        ocr_requests_total.labels(status='error').inc()
        raise
```

## 性能调优检查清单

### 图片优化
- [ ] 图片尺寸 < 2048px
- [ ] 文件大小 < 1MB
- [ ] 使用 JPEG 格式
- [ ] 裁剪到金额区域

### 并发控制
- [ ] 设置合理的并发数 (≤10)
- [ ] 使用线程池或进程池
- [ ] 实现限速器
- [ ] 使用批量接口

### 超时配置
- [ ] 设置连接超时
- [ ] 设置读取超时
- [ ] 实现重试机制
- [ ] 使用指数退避

### 资源配置
- [ ] 设置内存限制
- [ ] 设置 CPU 限制
- [ ] 配置健康检查
- [ ] 设置重启策略

### 缓存策略
- [ ] 实现结果缓存
- [ ] 设置合理的 TTL
- [ ] 使用缓存键策略
- [ ] 定期清理缓存

### 监控分析
- [ ] 记录响应时间
- [ ] 监控资源使用
- [ ] 收集性能指标
- [ ] 设置告警规则

## 性能优化效果

实施上述优化后，预期效果：

| 优化项 | 优化前 | 优化后 | 提升 |
|-------|-------|-------|------|
| 响应时间 | 5-10s | 1-3s | 60-70% |
| 并发能力 | 3-5个 | 8-10个 | 100%+ |
| 内存使用 | 2-3GB | 1-2GB | 30-50% |
| 文件大小 | 3-5MB | <1MB | 70-80% |

---

[返回文档首页](./README.md)
