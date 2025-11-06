# 快速开始指南

本指南将帮助你快速搭建和运行 Cash Eye 金额识别服务。

## 目录

- [系统要求](#系统要求)
- [Docker 部署（推荐）](#docker-部署推荐)
- [本地开发环境](#本地开发环境)
- [配置说明](#配置说明)
- [验证安装](#验证安装)

## 系统要求

### 硬件要求

- **CPU**: 2核及以上
- **内存**: 最低 2GB，推荐 4GB
- **磁盘**: 至少 5GB 可用空间

### 软件要求

**Docker 部署:**
- Docker 20.10+
- Docker Compose 1.29+ (可选)

**本地开发:**
- Python 3.10+
- pip 21.0+
- Git

### 支持的操作系统

- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS 11+
- Windows 10/11 (WSL2 推荐)

## Docker 部署（推荐）

使用 Docker 是最简单、最可靠的部署方式。

### 1. 安装 Docker

如果尚未安装 Docker，请参考 [Docker 官方文档](https://docs.docker.com/get-docker/)。

验证 Docker 安装：
```bash
docker --version
```

### 2. 克隆项目

```bash
git clone https://github.com/your-org/cash-eye.git
cd cash-eye
```

### 3. 构建镜像

```bash
docker build -t money-ocr-api:1.0.0 .
```

构建过程需要 5-10 分钟，取决于网络速度。

### 4. 启动服务

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  money-ocr-api:1.0.0
```

### 5. 验证服务

```bash
# 检查容器状态
docker ps | grep money-ocr

# 健康检查
curl http://localhost:8000/api/v1/health
```

预期响应：
```json
{
  "status": "healthy",
  "service": "money-ocr-api",
  "version": "1.0.0"
}
```

### 使用 Docker Compose

如果你更喜欢使用 Docker Compose：

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 本地开发环境

适合需要修改代码或进行开发的场景。

### 1. 安装 Python

确保已安装 Python 3.10 或更高版本：

```bash
python --version
# 或
python3 --version
```

### 2. 克隆项目

```bash
git clone https://github.com/your-org/cash-eye.git
cd cash-eye
```

### 3. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 4. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖（如需开发和测试）
pip install -r requirements-dev.txt
```

### 5. 验证安装（可选）

运行验证脚本检查依赖是否正确安装：

```bash
python verify_install.py
```

### 6. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置（可选）
nano .env
```

### 7. 启动服务

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

参数说明：
- `--host 0.0.0.0`: 监听所有网络接口
- `--port 8000`: 服务端口
- `--reload`: 代码更改时自动重载（仅开发环境）

### 8. 验证服务

打开浏览器访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health

## 配置说明

### 环境变量

在 `.env` 文件中配置以下参数：

```bash
# 服务配置
PORT=8000
HOST=0.0.0.0

# 日志级别
# 可选值: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# 文件限制
MAX_FILE_SIZE_MB=10

# 超时配置
REQUEST_TIMEOUT_SEC=30
OCR_TIMEOUT_SEC=3

# 服务信息
SERVICE_NAME=money-ocr-api
SERVICE_VERSION=1.0.0
```

### 常用配置组合

**开发环境：**
```bash
LOG_LEVEL=DEBUG
PORT=8000
```

**生产环境：**
```bash
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
REQUEST_TIMEOUT_SEC=30
```

**性能优化：**
```bash
OCR_TIMEOUT_SEC=5
MAX_FILE_SIZE_MB=5
```

## 验证安装

### 1. 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

### 2. 测试 OCR 识别

准备一张包含金额的测试图片，然后：

```bash
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@test_invoice.jpg"
```

### 3. 查看 API 文档

浏览器访问 http://localhost:8000/docs 查看交互式 API 文档。

### 4. 运行测试套件（开发环境）

```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 生成测试图片
cd tests/fixtures
python generate_test_images.py
cd ../..

# 运行测试
pytest tests/ -v
```

## 常见问题

### Docker 相关

**Q: Docker 构建时出现网络错误？**

A: 可能是网络问题或防火墙限制。尝试：
- 使用国内镜像源
- 检查防火墙设置
- 使用代理

**Q: 容器启动后立即退出？**

A: 查看容器日志：
```bash
docker logs money-ocr
```

### Python 相关

**Q: pip install 失败？**

A: 尝试以下方案：
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: PaddleOCR 模型下载失败？**

A: 首次运行时 PaddleOCR 会下载模型文件。如果网络受限，请参考 [部署指南](./deployment.md) 中的离线部署方案。

### 其他问题

更多问题请查看 [问题排查指南](./troubleshooting.md)。

## 下一步

- 📖 阅读 [API 使用文档](./api-usage.md) 了解 API 详细用法
- 🚀 查看 [部署指南](./deployment.md) 了解生产环境部署
- ⚡ 参考 [性能优化](./performance.md) 提升服务性能
- 🧪 阅读 [测试指南](./testing.md) 学习如何测试

## 获取帮助

- 📝 查看 [问题排查](./troubleshooting.md)
- 💬 提交 [GitHub Issue](https://github.com/your-org/cash-eye/issues)
- 📧 联系维护团队

---

[返回文档首页](./README.md)
