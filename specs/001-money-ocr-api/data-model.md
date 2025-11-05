# Data Model: 金额识别OCR服务

**Date**: 2025-11-05
**Feature**: 金额识别OCR服务
**Branch**: 001-money-ocr-api

## 概述

本服务为无状态API服务,不涉及持久化存储。数据模型主要定义API请求/响应结构和内部处理对象。

---

## API数据模型

### 1. RecognitionRequest (识别请求)

**描述**: 单张图片识别请求

**字段**:

| 字段名 | 类型 | 必填 | 说明 | 验证规则 |
|--------|------|------|------|----------|
| file | File | ✅ | 图片文件 | 格式: jpeg/png/bmp/tiff<br>大小: ≤10MB |

**示例** (multipart/form-data):
```http
POST /api/v1/recognize
Content-Type: multipart/form-data

file=@image.jpg
```

---

### 2. BatchRecognitionRequest (批量识别请求)

**描述**: 多张图片批量识别请求

**字段**:

| 字段名 | 类型 | 必填 | 说明 | 验证规则 |
|--------|------|------|----------|----------|
| files | List[File] | ✅ | 图片文件列表 | 每个文件遵循RecognitionRequest验证规则<br>最大数量: 建议≤10张(避免超时) |

**示例** (multipart/form-data):
```http
POST /api/v1/recognize/batch
Content-Type: multipart/form-data

files=@image1.jpg
files=@image2.png
files=@image3.jpg
```

---

### 3. RecognitionResponse (识别响应 - 成功)

**描述**: 单张图片识别成功响应

**字段**:

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| success | boolean | ✅ | 请求是否成功 | `true` |
| data | RecognitionResult | ✅ | 识别结果数据 | 见下方 |

**RecognitionResult字段**:

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| amount | string \| null | ✅ | 识别出的金额(纯数字格式) | `"1234.56"` |
| confidence | float | ✅ | OCR识别置信度(0-1) | `0.95` |
| processing_time_ms | integer | ✅ | 处理耗时(毫秒) | `1234` |
| raw_text | string | ❌ | OCR原始文本(调试用) | `"¥1,234.56"` |
| warnings | List[string] | ❌ | 警告信息 | `["置信度较低"]` |

**示例响应**:
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

**无金额场景**:
```json
{
  "success": true,
  "data": {
    "amount": null,
    "confidence": 0.0,
    "processing_time_ms": 892,
    "raw_text": "",
    "warnings": ["未识别到金额"]
  }
}
```

---

### 4. BatchRecognitionResponse (批量识别响应)

**描述**: 批量识别响应

**字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| success | boolean | ✅ | 请求是否成功(至少一个成功即为true) |
| data | BatchRecognitionResult | ✅ | 批量结果数据 |

**BatchRecognitionResult字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| total | integer | ✅ | 总图片数量 |
| succeeded | integer | ✅ | 成功识别数量 |
| failed | integer | ✅ | 失败数量 |
| results | List[BatchItemResult] | ✅ | 每张图片的结果 |

**BatchItemResult字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| index | integer | ✅ | 图片索引(从0开始) |
| filename | string | ✅ | 原始文件名 |
| success | boolean | ✅ | 该图片是否成功 |
| data | RecognitionResult \| null | ✅ | 识别结果(成功时) |
| error | ErrorDetail \| null | ✅ | 错误信息(失败时) |

**示例响应**:
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
        "filename": "image1.jpg",
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
        "filename": "image2.png",
        "success": false,
        "data": null,
        "error": {
          "code": "FILE_TOO_LARGE",
          "message": "图片大小超过10MB限制",
          "details": "当前大小: 12.5MB"
        }
      },
      {
        "index": 2,
        "filename": "image3.jpg",
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

---

### 5. ErrorResponse (错误响应)

**描述**: API错误响应统一格式

**字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| success | boolean | ✅ | 固定为`false` |
| error | ErrorDetail | ✅ | 错误详情 |

**ErrorDetail字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | ✅ | 错误码(大写下划线命名) |
| message | string | ✅ | 人类可读的错误信息 |
| details | string | ❌ | 详细错误信息(调试用) |

**错误码定义**:

| 错误码 | HTTP状态码 | 说明 | 示例message |
|--------|-----------|------|-------------|
| `FILE_TOO_LARGE` | 413 | 文件超过10MB | "图片大小超过10MB限制" |
| `UNSUPPORTED_FORMAT` | 400 | 不支持的图片格式 | "仅支持JPEG、PNG、BMP、TIFF格式" |
| `INVALID_IMAGE` | 400 | 图片文件损坏 | "无法解析图片文件" |
| `NO_FILE_PROVIDED` | 400 | 未提供文件 | "请上传图片文件" |
| `OCR_ENGINE_ERROR` | 500 | OCR引擎内部错误 | "OCR处理失败" |
| `TIMEOUT` | 504 | 处理超时 | "图片处理超时(>3秒)" |
| `INTERNAL_ERROR` | 500 | 未知内部错误 | "服务器内部错误" |

**示例响应**:
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "图片大小超过10MB限制",
    "details": "当前大小: 12.5MB, 限制: 10MB"
  }
}
```

---

### 6. HealthCheckResponse (健康检查响应)

**描述**: 服务健康状态响应

**字段**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | ✅ | 服务状态: `"healthy"` \| `"unhealthy"` |
| service | string | ✅ | 服务名称 |
| version | string | ✅ | 服务版本号 |
| ocr_engine | string | ✅ | OCR引擎名称 |
| uptime_seconds | integer | ✅ | 运行时长(秒) |
| error | string | ❌ | 错误信息(异常时) |

**健康响应示例**:
```json
{
  "status": "healthy",
  "service": "money-ocr-api",
  "version": "1.0.0",
  "ocr_engine": "paddleocr-2.7.0",
  "uptime_seconds": 86400
}
```

**异常响应示例**:
```json
{
  "status": "unhealthy",
  "service": "money-ocr-api",
  "version": "1.0.0",
  "ocr_engine": "paddleocr-2.7.0",
  "uptime_seconds": 3600,
  "error": "OCR引擎初始化失败"
}
```

---

## 内部数据模型

### 7. ImageMetadata (图片元数据)

**描述**: 内部使用的图片元信息

**字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| filename | string | 原始文件名 |
| format | string | 图片格式(jpeg/png/bmp/tiff) |
| size_bytes | integer | 文件大小(字节) |
| width | integer | 图片宽度(像素) |
| height | integer | 图片高度(像素) |
| mode | string | 颜色模式(RGB/RGBA/L等) |

---

### 8. OCRResult (OCR原始结果)

**描述**: PaddleOCR返回的原始结果

**结构**:
```python
# PaddleOCR返回格式
[
    [  # 第一个文本块
        [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 坐标
        ("1234.56", 0.95)  # (文本, 置信度)
    ],
    [  # 第二个文本块
        [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
        ("¥", 0.88)
    ]
]
```

**处理逻辑**:
1. 提取所有文本块的`(文本, 置信度)`
2. 拼接文本,计算平均置信度
3. 传递给金额提取器

---

## 数据流转图

```
客户端
  |
  | (1) POST /api/v1/recognize (multipart/form-data)
  v
API路由层 (routes.py)
  |
  | (2) 验证文件格式、大小
  v
图片处理器 (image_processor.py)
  |
  | (3) 预处理: 格式转换、压缩、增强
  v
OCR服务 (ocr_service.py)
  |
  | (4) PaddleOCR识别 → OCRResult
  v
金额提取器 (ocr_service.py)
  |
  | (5) 正则提取 → amount字符串
  v
响应构建器 (routes.py)
  |
  | (6) RecognitionResponse JSON
  v
客户端
```

---

## 验证规则总结

### 请求验证:

1. **文件存在性**: 必须提供`file`字段
2. **文件大小**: ≤10MB (10 * 1024 * 1024 bytes)
3. **文件格式**: MIME类型为`image/jpeg`、`image/png`、`image/bmp`、`image/tiff`
4. **批量数量**: 建议≤10张(前端限制)

### 响应验证:

1. **amount格式**: 匹配正则`^\d+(\.\d{1,2})?$`(整数或最多2位小数)
2. **confidence范围**: 0.0 ≤ confidence ≤ 1.0
3. **processing_time**: 正整数,单位毫秒

---

## 扩展考虑

### 未来可能扩展:

1. **多币种支持**: 返回`currency_code`字段(如"CNY", "USD")
2. **位置信息**: 返回金额在图片中的坐标(OCRResult中已包含)
3. **多金额返回**: 修改为返回`amounts: List[string]`而非单一金额
4. **置信度阈值**: 允许客户端指定最低置信度过滤

### 向后兼容性:

- 新增字段必须为可选字段
- 错误码体系保持稳定,新增错误码不影响现有逻辑
- API版本化路径(`/api/v1/`)便于未来V2迭代
