# API 使用文档

本文档详细介绍 Cash Eye API 的使用方法和最佳实践。

## 目录

- [API 概览](#api-概览)
- [认证](#认证)
- [接口详解](#接口详解)
  - [健康检查](#健康检查)
  - [单张图片识别](#单张图片识别)
  - [批量图片识别](#批量图片识别)
- [客户端示例](#客户端示例)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)

## API 概览

### 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **数据格式**: JSON
- **请求方式**:
  - 图片上传：`multipart/form-data`
  - 健康检查：`GET`

### 交互式文档

启动服务后，可访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 认证

当前版本不需要认证。如需在生产环境中添加认证，建议使用：

- API Key
- OAuth 2.0
- JWT Token

## 接口详解

### 健康检查

检查服务是否正常运行。

**请求：**
```http
GET /api/v1/health
```

**响应：**
```json
{
  "status": "healthy",
  "service": "money-ocr-api",
  "version": "1.0.0"
}
```

**示例：**
```bash
curl http://localhost:8000/api/v1/health
```

---

### 单张图片识别

识别单张图片中的金额信息。

**请求：**
```http
POST /api/v1/recognize
Content-Type: multipart/form-data
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| file | File | 是 | 图片文件（JPEG/PNG/BMP/TIFF） |

**成功响应：**
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

**响应字段说明：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| success | boolean | 请求是否成功 |
| data.amount | string | 识别到的金额（数字格式） |
| data.confidence | float | 置信度（0.0-1.0） |
| data.processing_time_ms | int | 处理时间（毫秒） |
| data.raw_text | string | OCR 原始文本 |
| data.warnings | array | 警告信息列表 |

**示例：**

```bash
# cURL
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice.jpg"

# HTTPie
http -f POST http://localhost:8000/api/v1/recognize file@invoice.jpg
```

**错误响应：**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Only JPEG, PNG, BMP, and TIFF files are supported"
  }
}
```

---

### 批量图片识别

一次性识别多张图片。

**请求：**
```http
POST /api/v1/recognize/batch
Content-Type: multipart/form-data
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| files | File[] | 是 | 多个图片文件 |

**成功响应：**
```json
{
  "success": true,
  "data": {
    "total": 3,
    "succeeded": 2,
    "failed": 1,
    "results": [
      {
        "index": 0,
        "filename": "invoice1.jpg",
        "success": true,
        "data": {
          "amount": "1234.56",
          "confidence": 0.95,
          "processing_time_ms": 1200
        },
        "error": null
      },
      {
        "index": 1,
        "filename": "invoice2.png",
        "success": true,
        "data": {
          "amount": "5000.00",
          "confidence": 0.88,
          "processing_time_ms": 1500
        },
        "error": null
      },
      {
        "index": 2,
        "filename": "invalid.txt",
        "success": false,
        "data": null,
        "error": {
          "code": "INVALID_FILE_FORMAT",
          "message": "Unsupported file format"
        }
      }
    ]
  }
}
```

**示例：**

```bash
curl -X POST http://localhost:8000/api/v1/recognize/batch \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.png" \
  -F "files=@invoice3.jpg"
```

**限制：**
- 建议每次最多上传 10 张图片
- 单个文件最大 10MB
- 总请求超时 30 秒

---

## 客户端示例

### Python

#### 基础示例

```python
import requests

def recognize_amount(image_path):
    """识别单张图片中的金额"""
    url = "http://localhost:8000/api/v1/recognize"

    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)

    result = response.json()

    if result["success"]:
        data = result["data"]
        print(f"金额: {data['amount']}")
        print(f"置信度: {data['confidence']}")
        print(f"处理时间: {data['processing_time_ms']}ms")
        return data["amount"]
    else:
        error = result["error"]
        print(f"识别失败: {error['message']}")
        return None

# 使用
amount = recognize_amount("invoice.jpg")
```

#### 批量识别

```python
import requests
from pathlib import Path

def recognize_batch(image_paths):
    """批量识别图片"""
    url = "http://localhost:8000/api/v1/recognize/batch"

    files = [
        ("files", (Path(p).name, open(p, "rb"), "image/jpeg"))
        for p in image_paths
    ]

    response = requests.post(url, files=files)
    result = response.json()

    if result["success"]:
        data = result["data"]
        print(f"总数: {data['total']}, 成功: {data['succeeded']}, 失败: {data['failed']}")

        for item in data["results"]:
            if item["success"]:
                print(f"{item['filename']}: {item['data']['amount']}")
            else:
                print(f"{item['filename']}: 错误 - {item['error']['message']}")

        return data["results"]

    return None

# 使用
results = recognize_batch([
    "invoice1.jpg",
    "invoice2.png",
    "invoice3.jpg"
])
```

#### 完整客户端类

```python
import requests
from typing import Optional, List, Dict
from pathlib import Path

class MoneyOCRClient:
    """Cash Eye API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            return response.status_code == 200
        except:
            return False

    def recognize(self, image_path: str, timeout: int = 10) -> Optional[Dict]:
        """识别单张图片"""
        url = f"{self.base_url}/api/v1/recognize"

        with open(image_path, "rb") as f:
            files = {"file": (Path(image_path).name, f)}
            response = self.session.post(url, files=files, timeout=timeout)

        result = response.json()
        return result if result["success"] else None

    def recognize_batch(self, image_paths: List[str], timeout: int = 30) -> Optional[Dict]:
        """批量识别"""
        url = f"{self.base_url}/api/v1/recognize/batch"

        files = [
            ("files", (Path(p).name, open(p, "rb")))
            for p in image_paths
        ]

        response = self.session.post(url, files=files, timeout=timeout)
        result = response.json()
        return result if result["success"] else None

# 使用示例
client = MoneyOCRClient()

# 健康检查
if client.health_check():
    print("服务正常")

# 单张识别
result = client.recognize("invoice.jpg")
if result:
    print(f"金额: {result['data']['amount']}")

# 批量识别
batch_result = client.recognize_batch([
    "invoice1.jpg",
    "invoice2.png"
])
```

### JavaScript / Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function recognizeAmount(imagePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(imagePath));

    try {
        const response = await axios.post(
            'http://localhost:8000/api/v1/recognize',
            form,
            { headers: form.getHeaders() }
        );

        if (response.data.success) {
            const { amount, confidence } = response.data.data;
            console.log(`金额: ${amount}`);
            console.log(`置信度: ${confidence}`);
            return amount;
        }
    } catch (error) {
        console.error('识别失败:', error.message);
        return null;
    }
}

// 使用
recognizeAmount('invoice.jpg');
```

### cURL

```bash
# 单张识别
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice.jpg" \
  -H "Accept: application/json"

# 批量识别
curl -X POST http://localhost:8000/api/v1/recognize/batch \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.png"

# 健康检查
curl http://localhost:8000/api/v1/health
```

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 说明 |
|-------|------------|------|
| INVALID_FILE_FORMAT | 400 | 不支持的文件格式 |
| FILE_TOO_LARGE | 413 | 文件超过大小限制 |
| NO_FILE_PROVIDED | 400 | 未提供文件 |
| OCR_FAILED | 500 | OCR 识别失败 |
| TIMEOUT | 504 | 请求超时 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### Python 错误处理示例

```python
import requests
from requests.exceptions import Timeout, ConnectionError

def safe_recognize(image_path):
    """带完整错误处理的识别"""
    url = "http://localhost:8000/api/v1/recognize"

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, timeout=10)

        response.raise_for_status()  # 检查 HTTP 错误
        result = response.json()

        if result["success"]:
            return result["data"]
        else:
            error = result["error"]
            print(f"API 错误 [{error['code']}]: {error['message']}")
            return None

    except FileNotFoundError:
        print(f"文件不存在: {image_path}")
    except Timeout:
        print("请求超时，请稍后重试")
    except ConnectionError:
        print("无法连接到服务器")
    except Exception as e:
        print(f"未知错误: {str(e)}")

    return None
```

## 最佳实践

### 1. 图片预处理

识别前对图片进行预处理可提升准确率：

```python
from PIL import Image

def optimize_image(input_path, output_path, max_size=2048):
    """优化图片以提升识别效果"""
    img = Image.open(input_path)

    # 转换为 RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 压缩大图
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 保存
    img.save(output_path, 'JPEG', quality=85, optimize=True)

# 使用
optimize_image("large_invoice.jpg", "optimized.jpg")
result = recognize_amount("optimized.jpg")
```

### 2. 并发控制

使用线程池控制并发数：

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def recognize_concurrent(image_paths, max_workers=5):
    """并发识别多张图片"""
    url = "http://localhost:8000/api/v1/recognize"

    def process_image(path):
        files = {"file": open(path, "rb")}
        response = requests.post(url, files=files)
        return response.json()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_image, image_paths))

    return results
```

### 3. 重试机制

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retries():
    """创建带重试的 Session"""
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
response = session.post(url, files=files, timeout=10)
```

### 4. 超时设置

```python
# 推荐超时配置
TIMEOUT_CONFIG = {
    "single": 10,   # 单张图片 10 秒
    "batch": 30,    # 批量图片 30 秒
}

response = requests.post(
    url,
    files=files,
    timeout=TIMEOUT_CONFIG["single"]
)
```

### 5. 置信度阈值

```python
def recognize_with_threshold(image_path, min_confidence=0.8):
    """识别并过滤低置信度结果"""
    result = recognize_amount(image_path)

    if result and result["data"]["confidence"] >= min_confidence:
        return result["data"]["amount"]
    else:
        print("置信度过低，建议人工复核")
        return None
```

## 性能优化建议

1. **图片大小**: 控制在 2048px 以内，< 1MB
2. **并发数**: 单实例最多 10 个并发请求
3. **批量大小**: 每次批量最多 10 张图片
4. **超时设置**: 单张 10s，批量 30s
5. **重试策略**: 最多重试 3 次，指数退避

更多性能优化详见 [性能优化文档](./performance.md)。

---

[返回文档首页](./README.md)
