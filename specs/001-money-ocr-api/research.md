# Research: 金额识别OCR服务

**Date**: 2025-11-05
**Feature**: 金额识别OCR服务
**Branch**: 001-money-ocr-api

## Research Tasks

本研究阶段解决技术选型和最佳实践问题。

---

## 1. Web框架选型: FastAPI vs Flask

### 决策: FastAPI

### 理由:

1. **性能优势**:
   - 基于Starlette和Pydantic,性能接近Go/Node.js
   - 原生支持异步(async/await),适合I/O密集型OCR任务
   - 支持并发请求处理,符合"至少10个并发"的需求

2. **开发效率**:
   - 自动生成OpenAPI(Swagger)文档,满足API规范需求
   - 内置请求验证(Pydantic模型),减少手动验证代码
   - 类型提示支持,IDE友好,减少bug

3. **现代化特性**:
   - 支持文件上传验证(大小、格式检查)
   - 内置依赖注入系统
   - 生产就绪(Uvicorn ASGI服务器)

4. **社区活跃**:
   - GitHub 70k+ stars
   - 丰富的插件生态(监控、日志、中间件)
   - 完善的文档和示例

### 考虑的替代方案:

| 框架 | 优势 | 劣势 | 拒绝原因 |
|------|------|------|----------|
| Flask | 简单轻量,成熟稳定 | 同步框架,性能较低,需要手动集成OpenAPI | 性能不足以支持10+并发,缺少现代化特性 |
| Django | 功能全面,管理后台 | 过重(ORM/模板引擎等),启动慢 | 违反简单性原则,不需要ORM和模板 |
| Tornado | 异步支持 | 社区较小,文档不如FastAPI | 没有FastAPI的开发效率优势 |

### 技术验证:

```python
# FastAPI示例 - 符合需求的简洁性
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI()

class OCRResponse(BaseModel):
    amount: str
    confidence: float
    processing_time: float

@app.post("/recognize", response_model=OCRResponse)
async def recognize_amount(file: UploadFile = File(...)):
    # 异步处理OCR
    pass
```

---

## 2. PaddleOCR集成最佳实践

### 决策: 使用PaddleOCR v3.3.1 (2025-10-29发布)

### 理由:

**版本确认** (2025-11-05): PaddleOCR v3.3.1于2025年10月29日正式发布,这是基于PP-OCRv5模型的最新稳定版本,完全满足用户要求。

**版本优势**:
- 最新的PP-OCRv5模型,识别准确率更高
- 稳定的生产版本,经过充分测试
- 完整的文档和社区支持
- CPU模式性能优化

### 集成策略:

1. **初始化优化**:
   ```python
   from paddleocr import PaddleOCR

   # 全局单例,避免重复加载模型(加速响应)
   ocr_engine = PaddleOCR(
       use_angle_cls=True,      # 支持旋转图片
       lang='ch',                # 中文+数字识别
       use_gpu=False,            # CPU模式
       show_log=False,           # 关闭调试日志
       det_model_dir=None,       # 使用默认模型
       rec_model_dir=None
   )
   ```

2. **数字识别优化**:
   - 使用`use_angle_cls=True`处理旋转图片
   - 配置`rec_char_type='number'`(如果仅识别数字)
   - 后处理:正则过滤非数字字符,提取金额格式

3. **性能优化**:
   - 预加载模型到内存(应用启动时)
   - 图片预处理:压缩大图(>2MB),灰度化,二值化
   - 设置超时:单张图片最多3秒

### 安装:

```bash
pip install paddleocr==3.3.1
```

### 内存管理:

- PaddleOCR v3.3.1模型大小: ~8-10MB(轻量级PP-OCRv5模型)
- 预估内存占用: 基础300MB + 每并发50MB
- 10并发峰值: ~800MB,符合轻量级约束

### 考虑的替代方案:

| 方案 | 优势 | 劣势 | 拒绝原因 |
|------|------|------|----------|
| Tesseract OCR | 开源,成熟 | 中文识别较差,需要训练 | 准确率无法达到95%要求 |
| EasyOCR | 支持80+语言 | 模型较大(>100MB),慢 | 违反轻量级和启动时间约束 |
| 云服务(阿里云/腾讯云) | 准确率高 | 网络依赖,成本 | 不符合Docker本地部署要求 |

---

## 3. 图片处理最佳实践

### 决策: 使用Pillow进行预处理

### 处理流程:

```python
from PIL import Image
import io

def preprocess_image(image_bytes: bytes) -> Image.Image:
    """图片预处理优化识别"""
    img = Image.open(io.BytesIO(image_bytes))

    # 1. 格式转换(统一为RGB)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 2. 尺寸优化(大图压缩,节省内存)
    max_dimension = 2048
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 3. 可选:锐化/对比度增强(提升模糊图片识别率)
    # from PIL import ImageEnhance
    # enhancer = ImageEnhance.Contrast(img)
    # img = enhancer.enhance(1.5)

    return img
```

### 格式支持验证:

- **JPEG**: ✅ Pillow原生支持
- **PNG**: ✅ Pillow原生支持
- **BMP**: ✅ Pillow原生支持
- **TIFF**: ✅ Pillow原生支持(可能需要`libtiff`)

### 安全考虑:

- 使用`Pillow`的安全模式防止图片炸弹攻击
- 限制解压后图片尺寸(防止内存溢出)
- 验证文件签名(防止伪造扩展名)

---

## 4. 金额提取策略

### 决策: 正则表达式 + 规则引擎

### 实现策略:

```python
import re
from typing import Optional

def extract_amount(ocr_text: str) -> Optional[str]:
    """从OCR文本中提取金额"""
    # 清理文本:去除空格、换行
    text = ocr_text.replace(' ', '').replace('\n', '')

    # 模式1: 带货币符号的金额 ¥1,234.56 / $1,234.56
    pattern1 = r'[¥$￥]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'

    # 模式2: 纯数字金额 1234.56 / 1,234.56
    pattern2 = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+\.\d{2}|\d+)'

    # 优先匹配带货币符号
    match = re.search(pattern1, text)
    if match:
        amount = match.group(1)
    else:
        match = re.search(pattern2, text)
        if match:
            amount = match.group(1)
        else:
            return None

    # 标准化:移除千分位逗号
    amount = amount.replace(',', '')

    # 验证:检查是否为合法金额格式
    if re.match(r'^\d+(\.\d{1,2})?$', amount):
        return amount

    return None
```

### 边界情况处理:

| 场景 | 处理策略 |
|------|----------|
| 多个金额 | 返回第一个匹配的金额(符合FR-013) |
| 无金额 | 返回`null`,错误码`NO_AMOUNT_FOUND` |
| 格式异常 | 尝试修复(如"1 234.56" → "1234.56") |
| 置信度低 | OCR结果<0.8时警告,但仍返回 |

---

## 5. 日志和监控方案

### 决策: structlog + 健康检查端点

### 日志策略:

```python
import structlog

logger = structlog.get_logger()

# 结构化日志示例
logger.info(
    "ocr_request",
    image_format="jpeg",
    image_size_kb=256,
    processing_time_ms=1234,
    confidence=0.95,
    amount="1234.56"
)
```

### 健康检查设计:

```python
@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查OCR引擎是否可用
        test_result = ocr_engine.ocr("test")

        return {
            "status": "healthy",
            "service": "money-ocr-api",
            "version": "1.0.0",
            "ocr_engine": "paddleocr",
            "uptime_seconds": get_uptime()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

### 监控指标:

- 请求总数、成功率、失败率
- 平均响应时间、P95/P99延迟
- OCR识别置信度分布
- 内存占用趋势

---

## 6. Docker镜像优化

### 决策: 多阶段构建 + Alpine基础镜像

### Dockerfile策略:

```dockerfile
# 阶段1: 构建依赖
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .

# 使用国内镜像加速
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt

# 阶段2: 运行镜像
FROM python:3.9-slim

WORKDIR /app

# 复制依赖
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# 安装PaddleOCR依赖的系统库
RUN apt-get update && apt-get install -y \
    libgomp1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制应用代码
COPY src/ ./src/
COPY main.py .

# 配置环境变量
ENV PORT=8000
ENV LOG_LEVEL=INFO

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 镜像优化目标:

- 镜像大小: <500MB(包含PaddleOCR模型)
- 启动时间: <30秒(符合SC-004)
- 使用`.dockerignore`排除测试文件、文档

---

## 7. 错误处理设计

### HTTP错误码映射:

| 场景 | HTTP状态码 | 错误码 | 说明 |
|------|-----------|--------|------|
| 文件过大 | 413 | FILE_TOO_LARGE | 超过10MB |
| 格式不支持 | 400 | UNSUPPORTED_FORMAT | 非JPEG/PNG/BMP/TIFF |
| 文件损坏 | 400 | INVALID_IMAGE | 无法解析图片 |
| 未识别到金额 | 200 | NO_AMOUNT_FOUND | 返回空结果+提示 |
| OCR引擎错误 | 500 | OCR_ENGINE_ERROR | 内部错误 |
| 超时 | 504 | TIMEOUT | 处理超过3秒 |

### 错误响应格式:

```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "图片大小超过10MB限制",
    "details": "当前大小: 12.5MB"
  }
}
```

---

## 研究总结

### 关键决策汇总:

1. **Web框架**: FastAPI (异步、性能、文档自动生成)
2. **OCR引擎**: PaddleOCR v2.7+ CPU模式 (符合约束)
3. **图片处理**: Pillow (轻量、支持所需格式)
4. **金额提取**: 正则表达式 + 规则清洗
5. **日志**: structlog 结构化日志
6. **部署**: Docker多阶段构建,Uvicorn ASGI服务器

### 风险和缓解措施:

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| CPU识别速度慢 | 无法达到3秒要求 | 图片预处理优化、模型预加载、PaddleOCR v3.3.1的CPU优化 |
| 内存泄漏 | 7天运行内存增长 | 仅内存处理不落盘、监控内存指标、必要时重启 |
| 并发超过10个 | 性能下降 | 单实例设计假设不超10并发,实际超限时返回503错误 |

### 下一步行动:

Phase 1将基于本研究生成:
- `data-model.md`: 数据模型定义
- `contracts/`: OpenAPI规范
- `quickstart.md`: 快速开始指南
