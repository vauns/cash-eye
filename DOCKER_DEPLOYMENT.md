# Docker 部署说明

本文档说明如何使用 Docker 部署 Cash Eye 服务，包括在线和离线两种模式。

## 快速开始

### 在线模式（默认）

适用于有网络连接的环境，模型会在首次运行时自动下载。

```bash
# 使用 docker
docker build -t money-ocr-api:1.0.0 .
docker run -d --name money-ocr -p 8000:8000 money-ocr-api:1.0.0

# 或使用 docker-compose
docker-compose up -d
```

### 离线模式

适用于内网或无网络环境，有两种方式：

#### 方式1：构建时打包模型（推荐）

```bash
# 1. 在有网络的环境准备模型
bash scripts/prepare_offline_deployment.sh

# 2. 构建包含模型的镜像
docker build --build-arg OFFLINE_BUILD=true -t money-ocr-api:offline .

# 或使用 docker-compose
OFFLINE_BUILD=true docker-compose up -d --build

# 3. 导出镜像（可选，用于传输）
docker save money-ocr-api:offline -o money-ocr-api-offline.tar

# 4. 在离线环境加载并运行
docker load -i money-ocr-api-offline.tar
docker run -d --name money-ocr -p 8000:8000 money-ocr-api:offline
```

#### 方式2：卷挂载模型

```bash
# 1. 准备模型目录
python scripts/download_models.py --model-dir ./models

# 2. 启动时挂载模型目录
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -v $(pwd)/models:/root/.paddlex/official_models:ro \
  money-ocr-api:1.0.0

# 或修改 docker-compose.yml 中的 volumes 配置后：
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|-------|-------|------|
| PORT | 8000 | 服务端口 |
| LOG_LEVEL | INFO | 日志级别 |
| MAX_FILE_SIZE_MB | 10 | 最大文件大小(MB) |
| REQUEST_TIMEOUT_SEC | 30 | 请求超时(秒) |
| OCR_TIMEOUT_SEC | 3 | OCR超时(秒) |

### 构建参数

| 参数名 | 默认值 | 说明 |
|-------|-------|------|
| OFFLINE_BUILD | false | 是否构建离线镜像 |

## 资源配置

### 推荐配置

- **CPU**: 2 核
- **内存**: 2GB
- **磁盘**: 5GB（包含模型）

### 使用 docker-compose 限制资源

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

或通过环境变量：

```bash
CPU_LIMIT=4.0 MEMORY_LIMIT=4G docker-compose up -d
```

## 验证部署

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 测试识别
curl -X POST http://localhost:8000/api/v1/recognize \
  -F "file=@test_image.jpg"
```

## 故障排查

### 容器启动失败

```bash
# 查看日志
docker logs money-ocr

# 检查资源
docker stats money-ocr
```

### 模型加载失败

```bash
# 检查模型目录
docker exec money-ocr ls -la /root/.paddlex/

# 查看模型加载日志
docker logs money-ocr 2>&1 | grep -i "model"
```

## 高级用法

### 多实例部署

```bash
# 启动多个实例
docker run -d --name money-ocr-1 -p 8001:8000 money-ocr-api:1.0.0
docker run -d --name money-ocr-2 -p 8002:8000 money-ocr-api:1.0.0
docker run -d --name money-ocr-3 -p 8003:8000 money-ocr-api:1.0.0

# 使用 Nginx 负载均衡
# 参考 docs/deployment.md 中的 Nginx 配置
```

### 自定义镜像

```bash
# 基于官方镜像定制
FROM money-ocr-api:1.0.0

# 添加自定义配置
COPY custom_config.py /app/config.py
ENV CUSTOM_VAR=value

# 重新构建
docker build -t my-money-ocr:1.0.0 .
```

## 参考文档

- [完整部署指南](./docs/deployment.md)
- [性能优化](./docs/performance.md)
- [问题排查](./docs/troubleshooting.md)

---

**提示**：详细的部署说明请参考 [docs/deployment.md](./docs/deployment.md)
