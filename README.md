# Cash Eye

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.3.1-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)

基于 PaddleOCR 的金额识别 HTTP API 服务

[快速开始](#快速开始) • [文档](#文档) • [API](#api-文档) • [贡献](#贡献)

</div>

---

## 功能特性

- ✨ **高精度识别** - 基于 PaddleOCR v3.3.1 (PP-OCRv5) 引擎
- 🚀 **简单易用** - RESTful API 设计，支持单张和批量识别
- 🐳 **容器化部署** - Docker 一键部署，支持离线环境
- 📊 **结构化输出** - 返回金额、置信度、处理时间等详细信息
- 📝 **完整日志** - structlog 结构化日志，便于监控和调试
- 🔧 **灵活配置** - 环境变量配置，适应不同场景需求

## 快速开始

### 使用 Docker（推荐）

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

# 2. 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 3. 运行测试
pip install -r requirements-dev.txt
pytest tests/
```

## 基本用法

### 识别单张图片

```bash
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@invoice.jpg"
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "amount": "1234.56",
    "confidence": 0.95,
    "processing_time_ms": 1234,
    "raw_text": "¥1,234.56"
  }
}
```

### Python 客户端

```python
import requests

url = "http://localhost:8000/api/v1/recognize"
files = {"file": open("invoice.jpg", "rb")}
response = requests.post(url, files=files)

result = response.json()
if result["success"]:
    print(f"识别金额: {result['data']['amount']}")
    print(f"置信度: {result['data']['confidence']}")
```

## 文档

完整文档请访问 [docs](./docs) 目录：

- **[快速开始指南](./docs/getting-started.md)** - 详细的安装和配置说明
- **[API 使用文档](./docs/api-usage.md)** - API 接口详解和客户端示例
- **[部署指南](./docs/deployment.md)** - Docker 部署、离线部署等
- **[测试指南](./docs/testing.md)** - 如何运行和编写测试
- **[性能优化](./docs/performance.md)** - 性能调优和最佳实践
- **[问题排查](./docs/troubleshooting.md)** - 常见问题和解决方案

## API 文档

服务启动后，可访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要接口

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/recognize` | POST | 单张图片识别 |
| `/api/v1/recognize/batch` | POST | 批量图片识别 |

## 技术栈

- **后端框架**: FastAPI
- **OCR 引擎**: PaddleOCR 3.3.1 (PP-OCRv5)
- **图像处理**: Pillow
- **Web 服务器**: Uvicorn
- **日志**: structlog
- **容器化**: Docker

## 支持的图片格式

- JPEG / JPG
- PNG
- BMP
- TIFF

## 贡献

欢迎贡献！请查看 [贡献指南](./CONTRIBUTING.md) 了解如何参与项目。

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件

## 项目状态

- ✅ 核心 OCR 功能
- ✅ RESTful API
- ✅ Docker 部署
- ✅ 离线部署支持
- ✅ 完整测试覆盖
- 🚧 性能监控仪表板（开发中）
- 🚧 多语言支持（计划中）

## 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 优秀的 OCR 工具包
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架

---

<div align="center">
Made with ❤️ by the Cash Eye Team
</div>
