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

### 批量识别

```bash
curl -X POST http://localhost:8000/api/v1/recognize/batch \
  -F "files=@invoice1.jpg" \
  -F "files=@invoice2.png"
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

## 详细文档

- [快速开始指南](./specs/001-money-ocr-api/quickstart.md)
- [API规范](./specs/001-money-ocr-api/contracts/openapi.yaml)
- [数据模型](./specs/001-money-ocr-api/data-model.md)
- [实施计划](./specs/001-money-ocr-api/plan.md)
