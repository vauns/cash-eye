# 金额识别OCR服务

基于PaddleOCR v3.3.1 (PP-OCRv5)的金额识别HTTP API服务。

## 功能特性

- 单张图片金额识别
- 批量图片金额识别
- 支持JPEG、PNG、BMP、TIFF格式
- Docker容器化部署
- 结构化日志输出
- 健康检查接口

## 快速开始

### 使用Docker部署(推荐)

```bash
# 构建镜像
docker build -t money-ocr-api:1.0.0 .

# 启动服务
docker run -d --name money-ocr -p 8000:8000 money-ocr-api:1.0.0

# 验证服务
curl http://localhost:8000/api/v1/health
```

### 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. 验证安装(可选)
python verify_install.py

# 3. 配置环境变量(可选)
cp .env.example .env
# 编辑.env文件修改配置

# 4. 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 5. 运行测试
pytest tests/
```

## API使用示例

### 识别单张图片

```bash
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice.jpg"
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "amount": "1234.56",
    "confidence": 0.95,
    "processing_time_ms": 1234,
    "raw_text": "¥1,234.56",
    "warnings": []
  }
}
```

### 批量识别

```bash
curl -X POST http://localhost:8000/api/v1/recognize/batch \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.png"
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "total": 2,
    "succeeded": 2,
    "failed": 0,
    "results": [
      {
        "index": 0,
        "filename": "invoice1.jpg",
        "success": true,
        "data": {
          "amount": "1234.56",
          "confidence": 0.95,
          "processing_time_ms": 1234
        },
        "error": null
      },
      {
        "index": 1,
        "filename": "invoice2.png",
        "success": true,
        "data": {
          "amount": "5000",
          "confidence": 0.88,
          "processing_time_ms": 2100
        },
        "error": null
      }
    ]
  }
}
```

### Python客户端示例

```python
import requests

# 单张图片识别
url = "http://localhost:8000/api/v1/recognize"
files = {"file": open("invoice.jpg", "rb")}
response = requests.post(url, files=files)
result = response.json()

if result["success"]:
    print(f"识别金额: {result['data']['amount']}")
    print(f"置信度: {result['data']['confidence']}")
else:
    print(f"识别失败: {result['error']['message']}")

# 批量识别
batch_url = "http://localhost:8000/api/v1/recognize/batch"
files = [
    ("files", open("invoice1.jpg", "rb")),
    ("files", open("invoice2.png", "rb"))
]
response = requests.post(batch_url, files=files)
result = response.json()

print(f"总数: {result['data']['total']}")
print(f"成功: {result['data']['succeeded']}")
print(f"失败: {result['data']['failed']}")
```

## API文档

服务启动后访问:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技术栈

- Python 3.9+
- FastAPI
- PaddleOCR 3.3.1 (PP-OCRv5)
- Pillow
- Uvicorn
- structlog

## 性能优化建议

### 图片预处理优化

在上传前对图片进行预处理可以显著提升识别速度和准确率:

```python
from PIL import Image

def optimize_image(input_path, output_path, max_size=2048):
    """优化图片大小和质量"""
    img = Image.open(input_path)

    # 转换为RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 压缩大图
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 保存为JPEG(压缩率更高)
    img.save(output_path, 'JPEG', quality=85, optimize=True)
```

**优化建议:**
- 图片分辨率控制在2048px以内
- 文件大小尽量<1MB
- 优先使用JPEG格式
- 裁剪图片只保留金额区域可提高准确率

### 并发控制最佳实践

使用Python客户端时,建议控制并发数量:

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def recognize_concurrent(image_paths, max_workers=5):
    """并发识别多张图片(控制并发数)"""
    url = "http://localhost:8000/api/v1/recognize"

    def process_image(path):
        files = {"file": open(path, "rb")}
        response = requests.post(url, files=files)
        return response.json()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_image, image_paths))

    return results

# 并发处理20张图片,最多5个并发
results = recognize_concurrent(image_list, max_workers=5)
```

**并发建议:**
- 单实例建议最多10个并发请求
- 批量接口建议每次最多10张图片
- 使用线程池控制并发数量
- 超过10个并发可能导致性能下降

### 超时和重试策略

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retries():
    """创建带重试的Session"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
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
    timeout=10  # 10秒超时
)
```

**超时配置:**
- 单张图片识别建议超时10秒
- 批量识别建议超时30秒
- OCR处理超过3秒会返回504错误
- 文件上传最大限制10MB

### 部署优化

**Docker资源限制:**
```yaml
# docker-compose.yml
services:
  money-ocr:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

**环境变量配置:**
```bash
# 生产环境推荐配置
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e MAX_FILE_SIZE_MB=10 \
  -e OCR_TIMEOUT_SEC=3 \
  -e REQUEST_TIMEOUT_SEC=30 \
  --restart unless-stopped \
  money-ocr-api:1.0.0
```

## 常见问题

### Q: 识别准确率低怎么办?

**A:** 尝试以下优化方法:
1. 提高图片分辨率(但不超过2048px)
2. 裁剪图片只保留金额区域
3. 调整图片对比度和亮度
4. 确保金额文字清晰无遮挡

### Q: 响应时间过长怎么办?

**A:** 检查以下方面:
1. 图片大小是否过大(建议<1MB)
2. 服务器CPU使用率是否过高
3. 是否有过多并发请求
4. 考虑使用批量接口减少网络开销

### Q: 服务内存占用过高?

**A:** 监控和优化措施:
1. 检查是否有图片未释放(应仅内存处理)
2. 控制并发数量(建议≤10)
3. 定期重启服务(Docker restart策略)
4. 监控内存增长趋势,7天内不应超过启动时150%

## 详细文档

- [快速开始指南](./specs/001-money-ocr-api/quickstart.md)
- [API规范](./specs/001-money-ocr-api/contracts/openapi.yaml)
- [数据模型](./specs/001-money-ocr-api/data-model.md)
- [实施计划](./specs/001-money-ocr-api/plan.md)

## 许可证

MIT License
