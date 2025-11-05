# Quick Start: 金额识别OCR服务

**版本**: 1.0.0
**最后更新**: 2025-11-05

## 概述

金额识别OCR服务是一个基于PaddleOCR的HTTP API服务,用于识别图片中的金额数字。本指南将帮助您在10分钟内完成部署和测试。

---

## 前置要求

- **Docker**: 20.10+ (必须)
- **操作系统**: Linux/macOS/Windows(带WSL2)
- **网络**: 访问Docker Hub或内网镜像仓库

---

## 快速部署 (Docker)

### 方式1: 使用预构建镜像 (推荐)

```bash
# 1. 拉取镜像
docker pull money-ocr-api:1.0.0

# 2. 启动服务(默认8000端口)
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  money-ocr-api:1.0.0

# 3. 验证服务启动
curl http://localhost:8000/api/v1/health
```

**预期输出**:
```json
{
  "status": "healthy",
  "service": "money-ocr-api",
  "version": "1.0.0",
  "ocr_engine": "paddleocr-2.7.0",
  "uptime_seconds": 12
}
```

### 方式2: 从源码构建

```bash
# 1. 克隆代码仓库
git clone <repository-url>
cd money-ocr-api

# 2. 构建Docker镜像
docker build -t money-ocr-api:1.0.0 .

# 3. 启动服务
docker run -d --name money-ocr -p 8000:8000 money-ocr-api:1.0.0
```

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `PORT` | 8000 | 服务监听端口 |
| `LOG_LEVEL` | INFO | 日志级别(DEBUG/INFO/WARNING/ERROR) |
| `MAX_FILE_SIZE_MB` | 10 | 最大文件大小(MB) |
| `REQUEST_TIMEOUT_SEC` | 30 | 请求超时时间(秒) |

**自定义配置示例**:
```bash
docker run -d \
  --name money-ocr \
  -p 9000:9000 \
  -e PORT=9000 \
  -e LOG_LEVEL=DEBUG \
  -e MAX_FILE_SIZE_MB=5 \
  money-ocr-api:1.0.0
```

---

## 使用示例

### 1. 单张图片识别

#### 使用curl:

```bash
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice.jpg"
```

**响应示例**:
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

#### 使用Python:

```python
import requests

url = "http://localhost:8000/api/v1/recognize"
files = {"file": open("invoice.jpg", "rb")}

response = requests.post(url, files=files)
result = response.json()

if result["success"]:
    print(f"识别金额: {result['data']['amount']}")
    print(f"置信度: {result['data']['confidence']}")
else:
    print(f"识别失败: {result['error']['message']}")
```

#### 使用JavaScript (Node.js):

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('invoice.jpg'));

axios.post('http://localhost:8000/api/v1/recognize', form, {
  headers: form.getHeaders()
})
.then(response => {
  const result = response.data;
  if (result.success) {
    console.log(`识别金额: ${result.data.amount}`);
    console.log(`置信度: ${result.data.confidence}`);
  }
})
.catch(error => {
  console.error('请求失败:', error.message);
});
```

---

### 2. 批量图片识别

#### 使用curl:

```bash
curl -X POST http://localhost:8000/api/v1/recognize/batch \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.png" \
  -F "files=@receipt.jpg"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 3,
    "succeeded": 3,
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
      },
      {
        "index": 2,
        "filename": "receipt.jpg",
        "success": true,
        "data": {
          "amount": "789.00",
          "confidence": 0.92,
          "processing_time_ms": 1567
        },
        "error": null
      }
    ]
  }
}
```

#### 使用Python:

```python
import requests

url = "http://localhost:8000/api/v1/recognize/batch"
files = [
    ("files", open("invoice1.jpg", "rb")),
    ("files", open("invoice2.png", "rb")),
    ("files", open("receipt.jpg", "rb"))
]

response = requests.post(url, files=files)
result = response.json()

print(f"总数: {result['data']['total']}")
print(f"成功: {result['data']['succeeded']}")
print(f"失败: {result['data']['failed']}")

for item in result['data']['results']:
    if item['success']:
        print(f"{item['filename']}: {item['data']['amount']}")
    else:
        print(f"{item['filename']}: 失败 - {item['error']['message']}")
```

---

### 3. 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "money-ocr-api",
  "version": "1.0.0",
  "ocr_engine": "paddleocr-2.7.0",
  "uptime_seconds": 86400
}
```

---

## 常见场景

### 场景1: 识别发票总额

```bash
# 上传发票图片
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice_total.jpg"

# 预期返回
{
  "success": true,
  "data": {
    "amount": "12345.67",
    "confidence": 0.96,
    "processing_time_ms": 1456
  }
}
```

### 场景2: 识别转账截图

```bash
# 上传微信/支付宝转账截图
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@wechat_transfer.png"

# 预期返回
{
  "success": true,
  "data": {
    "amount": "520.00",
    "confidence": 0.94,
    "processing_time_ms": 1123
  }
}
```

### 场景3: 处理模糊图片

```bash
# 上传模糊或低质量图片
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@blurry_receipt.jpg"

# 可能返回低置信度警告
{
  "success": true,
  "data": {
    "amount": "789.12",
    "confidence": 0.68,
    "processing_time_ms": 2345,
    "warnings": ["置信度较低,建议人工复核"]
  }
}
```

---

## 错误处理

### 错误响应格式

所有错误响应遵循统一格式:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "人类可读的错误信息",
    "details": "详细错误描述(可选)"
  }
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 说明 | 解决方案 |
|--------|-----------|------|----------|
| `FILE_TOO_LARGE` | 413 | 文件超过10MB | 压缩图片或调整`MAX_FILE_SIZE_MB` |
| `UNSUPPORTED_FORMAT` | 400 | 不支持的格式 | 使用JPEG/PNG/BMP/TIFF格式 |
| `INVALID_IMAGE` | 400 | 图片损坏 | 检查文件完整性 |
| `NO_FILE_PROVIDED` | 400 | 未提供文件 | 检查请求参数 |
| `TIMEOUT` | 504 | 处理超时 | 减小图片尺寸或增加超时时间 |
| `OCR_ENGINE_ERROR` | 500 | OCR引擎错误 | 检查服务日志,重启服务 |

### 错误处理示例 (Python)

```python
import requests

def recognize_amount(image_path):
    url = "http://localhost:8000/api/v1/recognize"
    files = {"file": open(image_path, "rb")}

    try:
        response = requests.post(url, files=files, timeout=10)
        result = response.json()

        if result["success"]:
            return result["data"]["amount"]
        else:
            error = result["error"]
            print(f"识别失败 [{error['code']}]: {error['message']}")
            return None
    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("无法连接到服务")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None

# 使用
amount = recognize_amount("invoice.jpg")
if amount:
    print(f"金额: {amount}")
```

---

## 性能优化建议

### 1. 图片预处理

在上传前对图片进行预处理可以提升识别速度和准确率:

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

optimize_image("large_invoice.png", "optimized.jpg")
```

### 2. 批量处理

对于多张图片,使用批量接口可以减少网络开销:

```python
# ❌ 不推荐: 多次单张请求
for image in images:
    response = requests.post(url, files={"file": open(image, "rb")})

# ✅ 推荐: 使用批量接口
files = [("files", open(image, "rb")) for image in images]
response = requests.post(batch_url, files=files)
```

### 3. 并发控制

建议控制并发请求数量:

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

---

## 监控和日志

### 查看服务日志

```bash
# 实时查看日志
docker logs -f money-ocr

# 查看最近100行日志
docker logs --tail 100 money-ocr
```

### 日志格式

服务使用结构化日志(JSON格式):

```json
{
  "event": "ocr_request",
  "timestamp": "2025-11-05T10:30:45.123Z",
  "level": "info",
  "image_format": "jpeg",
  "image_size_kb": 256,
  "processing_time_ms": 1234,
  "confidence": 0.95,
  "amount": "1234.56"
}
```

### 监控指标

推荐监控以下指标:

- **请求率**: 每分钟请求数
- **成功率**: 识别成功的百分比
- **响应时间**: P50/P95/P99延迟
- **错误率**: 各类错误码的分布
- **内存占用**: 防止内存泄漏

---

## 故障排查

### 问题1: 服务无法启动

**症状**: `docker run`后容器立即退出

**排查**:
```bash
# 查看容器日志
docker logs money-ocr

# 检查端口占用
netstat -tuln | grep 8000
```

**常见原因**:
- 端口已被占用 → 更换端口
- 内存不足 → 增加Docker内存限制
- 镜像损坏 → 重新拉取镜像

### 问题2: 识别准确率低

**排查清单**:
- [ ] 图片质量是否清晰?
- [ ] 金额是否被遮挡或模糊?
- [ ] 图片是否旋转或倾斜?
- [ ] 是否包含复杂背景?

**优化建议**:
- 提高图片分辨率(但不超过2048像素)
- 裁剪图片,只保留金额区域
- 调整图片对比度和亮度

### 问题3: 响应时间过长

**排查**:
```bash
# 测试响应时间
time curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@test.jpg"
```

**优化方案**:
- 压缩图片到<1MB
- 检查服务器CPU使用率
- 增加服务实例数量(负载均衡)

---

## Docker Compose部署

适用于生产环境的多容器编排:

```yaml
# docker-compose.yml
version: '3.8'

services:
  money-ocr:
    image: money-ocr-api:1.0.0
    container_name: money-ocr
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - MAX_FILE_SIZE_MB=10
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

启动:
```bash
docker-compose up -d
```

---

## API文档

服务启动后,访问以下URL查看交互式API文档:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 下一步

- **生产部署**: 参考 [部署指南](./deployment.md)
- **开发文档**: 参考 [开发手册](./development.md)
- **API详细文档**: 查看 [contracts/openapi.yaml](./contracts/openapi.yaml)
- **数据模型**: 查看 [data-model.md](./data-model.md)

---

## 技术支持

遇到问题?

- 📧 Email: support@example.com
- 🐛 Issues: <repository-issues-url>
- 📖 文档: <documentation-url>
