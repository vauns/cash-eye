# 离线部署指南

本文档说明如何在无网络环境中部署 Money OCR API 服务。

## 目录

- [背景](#背景)
- [模型文件说明](#模型文件说明)
- [部署方案概览](#部署方案概览)
- [方案一：镜像打包方式（推荐生产环境）](#方案一镜像打包方式推荐生产环境)
- [方案二：卷挂载方式（推荐开发环境）](#方案二卷挂载方式推荐开发环境)
- [方案三：手动配置方式](#方案三手动配置方式)
- [常见问题](#常见问题)

---

## 背景

Money OCR API 使用 PaddleOCR 进行文字识别。默认情况下，PaddleOCR 在首次运行时会从网络下载以下模型：

- **PP-OCRv5_mobile_det**：文本检测模型（约 120MB）
- **PP-OCRv5_mobile_rec**：文本识别模型（约 30MB）

模型默认缓存在用户主目录：`~/.paddleocr/`

在内网环境或无法联网的服务器上，需要提前下载模型并打包到 Docker 镜像中，或通过卷挂载的方式提供给容器。

---

## 模型文件说明

### 模型类型

| 模型名称 | 用途 | 大小 | 推理速度 |
|---------|------|------|---------|
| PP-OCRv5_mobile_det | 文本检测 | ~120MB | ~120ms |
| PP-OCRv5_mobile_rec | 文本识别 | ~30MB | ~30ms |

### 存储位置

- **默认路径**：`~/.paddleocr/`（容器内为 `/root/.paddleocr/`）
- **环境变量控制**：通过 `HUB_HOME` 环境变量可以指定缓存目录

---

## 部署方案概览

| 方案 | 适用场景 | 优点 | 缺点 |
|-----|---------|------|------|
| 方案一：镜像打包 | 生产环境 | 一次构建，到处运行；镜像自包含 | 镜像体积较大 |
| 方案二：卷挂载 | 开发/测试环境 | 灵活，易于更新模型 | 需要维护模型文件目录 |
| 方案三：手动配置 | 特殊需求 | 完全可控 | 操作步骤较多 |

---

## 方案一：镜像打包方式（推荐生产环境）

此方案将模型文件打包到 Docker 镜像中，适合生产环境一次构建、多次部署的场景。

### 步骤 1：准备环境（联网环境）

在有网络连接的环境（开发机或构建服务器）执行以下操作。

#### 1.1 下载模型文件

使用自动化脚本下载模型：

```bash
# 下载模型并打包
bash scripts/prepare_offline_deployment.sh
```

执行后会：
- 将模型下载到 `./models` 目录
- 打包为 `paddleocr-models-offline.tar.gz`

或者手动下载：

```bash
# 手动下载到指定目录
python scripts/download_models.py --model-dir ./models
```

#### 1.2 验证模型文件

```bash
# 检查模型目录
ls -lh models/

# 应该看到类似以下内容：
# whl/
# ├── det/
# │   └── PP-OCRv5_mobile_det/
# │       ├── inference.pdiparams
# │       ├── inference.pdmodel
# │       └── ...
# └── rec/
#     └── PP-OCRv5_mobile_rec/
#         ├── inference.pdiparams
#         ├── inference.pdmodel
#         └── ...
```

### 步骤 2：构建离线镜像（联网环境）

#### 2.1 使用自动化脚本构建

```bash
# 构建并可选导出镜像
bash scripts/build_offline_image.sh
```

脚本会：
- 检查模型文件是否存在
- 使用 `Dockerfile.offline` 构建镜像
- 询问是否导出为 tar 文件

#### 2.2 手动构建

```bash
# 构建镜像
docker build -f Dockerfile.offline -t money-ocr-api:offline .

# 导出镜像
docker save money-ocr-api:offline -o money-ocr-api-offline.tar

# 检查导出的镜像大小
ls -lh money-ocr-api-offline.tar
```

### 步骤 3：部署到离线环境

#### 3.1 传输镜像文件

将 `money-ocr-api-offline.tar` 复制到离线服务器：

```bash
# 通过 U盘、内网文件服务器等方式传输
scp money-ocr-api-offline.tar user@offline-server:/path/to/
```

#### 3.2 加载镜像

在离线服务器上：

```bash
# 加载镜像
docker load -i money-ocr-api-offline.tar

# 验证镜像
docker images | grep money-ocr-api
```

#### 3.3 启动服务

```bash
# 使用 docker-compose 启动
docker-compose -f docker-compose.offline.yml up -d

# 或直接运行容器
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  money-ocr-api:offline
```

#### 3.4 验证服务

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 测试 OCR 功能
curl -X POST http://localhost:8000/api/v1/ocr \
  -F "file=@test_image.jpg"
```

---

## 方案二：卷挂载方式（推荐开发环境）

此方案通过卷挂载提供模型文件，适合开发和测试环境。

### 步骤 1：下载模型（联网环境）

```bash
# 下载模型到本地目录
python scripts/download_models.py --model-dir ./models

# 或使用准备脚本
bash scripts/prepare_offline_deployment.sh
```

### 步骤 2：传输模型目录

将整个 `models` 目录复制到离线服务器：

```bash
# 打包模型目录
tar -czf models.tar.gz models/

# 传输到离线服务器
scp models.tar.gz user@offline-server:/path/to/

# 在离线服务器解压
tar -xzf models.tar.gz
```

### 步骤 3：配置 docker-compose

编辑 `docker-compose.offline.yml`，取消卷挂载的注释：

```yaml
services:
  money-ocr:
    image: money-ocr-api:offline
    volumes:
      - ./models:/root/.paddleocr:ro  # 挂载模型目录
    # ... 其他配置
```

### 步骤 4：启动服务

```bash
# 确保模型目录在当前位置
ls -d models/

# 启动服务
docker-compose -f docker-compose.offline.yml up -d

# 查看日志
docker-compose -f docker-compose.offline.yml logs -f
```

---

## 方案三：手动配置方式

适用于特殊需求或自定义部署场景。

### 步骤 1：下载模型到自定义位置

```bash
# 下载到自定义目录
python scripts/download_models.py --model-dir /opt/paddleocr-models
```

### 步骤 2：运行容器时挂载

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -v /opt/paddleocr-models:/root/.paddleocr:ro \
  -e HUB_HOME=/root/.paddleocr \
  money-ocr-api:1.0.0
```

### 步骤 3：验证模型加载

```bash
# 查看容器日志，确认模型加载成功
docker logs money-ocr

# 应该看到类似以下日志：
# INFO - Loading text detection model: PP-OCRv5_mobile_det
# INFO - Loading text recognition model: PP-OCRv5_mobile_rec
# INFO - Models loaded successfully
```

---

## 常见问题

### Q1: 如何确认模型已正确加载？

**A:** 查看容器启动日志：

```bash
docker logs money-ocr 2>&1 | grep -i "model"
```

成功加载会显示：
```
INFO - Text detection model loaded
INFO - Text recognition model loaded
```

如果模型缺失，会尝试下载并报错：
```
ERROR - Failed to download model
ERROR - No network connection
```

### Q2: 离线镜像大小是多少？

**A:**

- 基础镜像：约 400MB（Python 3.9-slim + 系统依赖）
- Python 包：约 500MB（PaddlePaddle + PaddleOCR + 其他依赖）
- 模型文件：约 150MB
- **总计**：约 1GB

### Q3: 可以使用更大的模型吗？

**A:** 可以，修改 `src/services/ocr_service.py:62,70` 中的模型名称：

```python
# 使用标准模型（更准确但更慢）
self.text_detector = TextDetection(
    model_name='PP-OCRv5_det',  # 标准检测模型
    ...
)

self.text_recognizer = TextRecognition(
    model_name='PP-OCRv5_rec',  # 标准识别模型
    ...
)
```

然后重新下载模型并构建镜像。

### Q4: 如何更新模型文件？

**A:**

方案一（镜像打包）：
1. 删除旧模型：`rm -rf models/`
2. 重新下载：`bash scripts/prepare_offline_deployment.sh`
3. 重新构建镜像：`bash scripts/build_offline_image.sh`

方案二（卷挂载）：
1. 删除旧模型：`rm -rf models/`
2. 重新下载：`python scripts/download_models.py --model-dir ./models`
3. 重启容器：`docker-compose -f docker-compose.offline.yml restart`

### Q5: 能否在容器启动时自动下载模型？

**A:** 可以，但不推荐用于离线环境。可以添加启动脚本：

```bash
# entrypoint.sh
#!/bin/bash
if [ ! -d "/root/.paddleocr/whl" ]; then
    echo "Downloading models..."
    python scripts/download_models.py
fi
exec "$@"
```

但这需要网络连接，不适合真正的离线环境。

### Q6: 模型文件损坏怎么办？

**A:** 删除模型缓存并重新下载：

```bash
# 在宿主机或容器内
rm -rf ~/.paddleocr/
python scripts/download_models.py
```

### Q7: 如何减小镜像体积？

**A:**

1. 使用 multi-stage 构建（已实现）
2. 使用 alpine 基础镜像（可能遇到兼容性问题）
3. 只安装必要的系统依赖
4. 使用模型压缩或量化（需修改代码）

---

## 脚本说明

### `scripts/download_models.py`

下载 PaddleOCR 模型到指定目录。

**用法：**
```bash
python scripts/download_models.py [--model-dir <directory>]
```

### `scripts/prepare_offline_deployment.sh`

自动化准备离线部署：下载模型并打包。

**用法：**
```bash
bash scripts/prepare_offline_deployment.sh
```

### `scripts/build_offline_image.sh`

构建包含模型的离线 Docker 镜像。

**用法：**
```bash
bash scripts/build_offline_image.sh
```

---

## 相关文件

- `Dockerfile.offline`：离线部署 Dockerfile
- `docker-compose.offline.yml`：离线部署 docker-compose 配置
- `.dockerignore.offline`：离线构建时的忽略规则

---

## 技术细节

### PaddleOCR 模型缓存机制

PaddleOCR 使用 PaddleHub 管理模型：

1. 检查本地缓存（`$HUB_HOME` 或 `~/.paddleocr/`）
2. 如果不存在，从远程下载
3. 解压到缓存目录
4. 加载模型进行推理

### 环境变量

| 变量名 | 作用 | 默认值 |
|-------|------|-------|
| `HUB_HOME` | 模型缓存目录 | `~/.paddleocr/` |
| `PADDLE_HOME` | PaddlePaddle 配置目录 | `~/.paddle/` |

### Dockerfile 关键配置

```dockerfile
# 复制模型到容器
COPY models/ /root/.paddleocr/

# 设置模型缓存目录
ENV HUB_HOME=/root/.paddleocr
```

---

## 获取帮助

如遇到问题，请：

1. 查看容器日志：`docker logs <container_name>`
2. 检查模型目录：`docker exec <container_name> ls -la /root/.paddleocr/`
3. 验证服务健康：`curl http://localhost:8000/api/v1/health`
4. 查看项目 Issues 或联系维护者

---

**最后更新**：2025-11-06
