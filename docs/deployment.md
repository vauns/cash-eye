# 部署指南

本文档介绍如何在不同环境中部署 Cash Eye 服务。

## 目录

- [部署方式概览](#部署方式概览)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [离线环境部署](#离线环境部署)
- [Docker Compose 部署](#docker-compose-部署)
- [Kubernetes 部署](#kubernetes-部署)
- [环境配置](#环境配置)

## 部署方式概览

| 部署方式 | 适用场景 | 难度 | 推荐度 |
|---------|---------|------|-------|
| Docker | 开发/测试/生产 | ⭐ | ⭐⭐⭐⭐⭐ |
| Docker Compose | 多服务编排 | ⭐⭐ | ⭐⭐⭐⭐ |
| 离线部署 | 内网/无网环境 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Kubernetes | 大规模集群 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 本地运行 | 开发调试 | ⭐ | ⭐⭐⭐ |

## Docker 部署

### 基础部署

```bash
# 1. 构建镜像
docker build -t money-ocr-api:1.0.0 .

# 2. 启动容器
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  money-ocr-api:1.0.0

# 3. 验证服务
curl http://localhost:8000/api/v1/health
```

### 带配置的部署

```bash
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

### 挂载日志目录

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -v /var/log/money-ocr:/app/logs \
  money-ocr-api:1.0.0
```

## 生产环境部署

### 资源限制

生产环境建议设置资源限制：

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  --memory="2g" \
  --cpus="2.0" \
  --restart unless-stopped \
  money-ocr-api:1.0.0
```

### 健康检查

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/api/v1/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --restart unless-stopped \
  money-ocr-api:1.0.0
```

### 反向代理（Nginx）

配置 Nginx 作为反向代理：

```nginx
# /etc/nginx/sites-available/money-ocr
server {
    listen 80;
    server_name ocr.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/money-ocr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### HTTPS 配置

使用 Let's Encrypt 配置 HTTPS：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d ocr.example.com

# 自动续期
sudo certbot renew --dry-run
```

## 离线环境部署

适用于内网或无法访问外网的环境。

### 背景说明

PaddleOCR 首次运行时需要下载以下模型（约 150MB）：
- **PP-OCRv5_mobile_det**: 文本检测模型 (~120MB)
- **PP-OCRv5_mobile_rec**: 文本识别模型 (~30MB)

模型默认缓存在 `~/.paddleocr/`

### 方案对比

| 方案 | 适用场景 | 优点 | 缺点 |
|-----|---------|------|------|
| 方案一：镜像打包 | 生产环境 | 一次构建，处处运行；镜像自包含 | 镜像体积较大 (~1GB) |
| 方案二：卷挂载 | 开发/测试环境 | 灵活，易于更新模型 | 需要维护模型目录 |
| 方案三：手动配置 | 特殊需求 | 完全可控 | 操作步骤较多 |

### 方案一：镜像打包方式（推荐）

将模型打包到 Docker 镜像中。

#### 步骤 1：准备环境（联网环境）

```bash
# 下载模型并打包
bash scripts/prepare_offline_deployment.sh
```

脚本会：
- 下载模型到 `./models` 目录
- 打包为 `paddleocr-models-offline.tar.gz`

或手动下载：
```bash
python scripts/download_models.py --model-dir ./models
```

#### 步骤 2：构建离线镜像

```bash
# 使用自动化脚本
bash scripts/build_offline_image.sh

# 或手动构建
docker build -f Dockerfile.offline -t money-ocr-api:offline .

# 导出镜像
docker save money-ocr-api:offline -o money-ocr-api-offline.tar
```

#### 步骤 3：部署到离线环境

```bash
# 1. 传输镜像文件到离线服务器
scp money-ocr-api-offline.tar user@offline-server:/path/to/

# 2. 加载镜像
docker load -i money-ocr-api-offline.tar

# 3. 启动服务
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  money-ocr-api:offline

# 4. 验证
curl http://localhost:8000/api/v1/health
```

### 方案二：卷挂载方式

通过卷挂载提供模型文件。

#### 步骤 1：下载模型（联网环境）

```bash
python scripts/download_models.py --model-dir ./models
```

#### 步骤 2：传输模型目录

```bash
# 打包
tar -czf models.tar.gz models/

# 传输
scp models.tar.gz user@offline-server:/path/to/

# 解压
tar -xzf models.tar.gz
```

#### 步骤 3：启动服务

```bash
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -v $(pwd)/models:/root/.paddleocr:ro \
  money-ocr-api:1.0.0
```

### 方案三：手动配置

```bash
# 1. 下载模型到自定义位置
python scripts/download_models.py --model-dir /opt/paddleocr-models

# 2. 运行容器时挂载
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -v /opt/paddleocr-models:/root/.paddleocr:ro \
  -e HUB_HOME=/root/.paddleocr \
  money-ocr-api:1.0.0
```

### 验证模型加载

```bash
# 查看容器日志
docker logs money-ocr 2>&1 | grep -i "model"
```

成功加载会显示：
```
INFO - Text detection model loaded
INFO - Text recognition model loaded
```

## Docker Compose 部署

### 基础配置

创建 `docker-compose.yml`：

```yaml
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
      - OCR_TIMEOUT_SEC=3
      - REQUEST_TIMEOUT_SEC=30
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

### 离线部署配置

创建 `docker-compose.offline.yml`：

```yaml
version: '3.8'

services:
  money-ocr:
    image: money-ocr-api:offline
    container_name: money-ocr-offline
    ports:
      - "8000:8000"
    volumes:
      # 可选：挂载模型目录
      # - ./models:/root/.paddleocr:ro
      # 可选：挂载日志目录
      # - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
      - HUB_HOME=/root/.paddleocr
    restart: unless-stopped
```

### 使用

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

## Kubernetes 部署

### Deployment

创建 `k8s/deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: money-ocr
  labels:
    app: money-ocr
spec:
  replicas: 3
  selector:
    matchLabels:
      app: money-ocr
  template:
    metadata:
      labels:
        app: money-ocr
    spec:
      containers:
      - name: money-ocr
        image: money-ocr-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: MAX_FILE_SIZE_MB
          value: "10"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Service

创建 `k8s/service.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: money-ocr-service
spec:
  selector:
    app: money-ocr
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 部署

```bash
# 应用配置
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 查看状态
kubectl get pods
kubectl get services

# 查看日志
kubectl logs -f deployment/money-ocr
```

## 环境配置

### 环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|-------|------|-------|------|
| PORT | 服务端口 | 8000 | 8080 |
| HOST | 监听地址 | 0.0.0.0 | 127.0.0.1 |
| LOG_LEVEL | 日志级别 | INFO | DEBUG |
| MAX_FILE_SIZE_MB | 最大文件大小(MB) | 10 | 20 |
| OCR_TIMEOUT_SEC | OCR 超时(秒) | 3 | 5 |
| REQUEST_TIMEOUT_SEC | 请求超时(秒) | 30 | 60 |
| HUB_HOME | 模型缓存目录 | ~/.paddleocr | /opt/models |

### 配置示例

**开发环境：**
```bash
LOG_LEVEL=DEBUG
PORT=8000
```

**生产环境：**
```bash
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
OCR_TIMEOUT_SEC=3
REQUEST_TIMEOUT_SEC=30
```

**高性能环境：**
```bash
LOG_LEVEL=WARNING
OCR_TIMEOUT_SEC=5
MAX_FILE_SIZE_MB=20
```

## 监控和日志

### 日志查看

```bash
# Docker 日志
docker logs money-ocr

# 实时日志
docker logs -f money-ocr

# 最近 100 行
docker logs --tail 100 money-ocr
```

### 资源监控

```bash
# 查看容器资源使用
docker stats money-ocr

# 查看详细信息
docker inspect money-ocr
```

### 健康检查

```bash
# 手动健康检查
curl http://localhost:8000/api/v1/health

# 自动健康检查（Docker）
docker inspect money-ocr | grep Health -A 10
```

## 故障排查

### 容器无法启动

```bash
# 查看错误日志
docker logs money-ocr

# 检查端口占用
netstat -tlnp | grep 8000

# 进入容器调试
docker exec -it money-ocr bash
```

### 模型加载失败

```bash
# 检查模型目录
docker exec money-ocr ls -la /root/.paddleocr/

# 查看模型加载日志
docker logs money-ocr 2>&1 | grep -i "model"
```

### 性能问题

```bash
# 查看资源使用
docker stats money-ocr

# 增加资源限制
docker update --memory="4g" --cpus="4.0" money-ocr
```

更多故障排查请参考 [问题排查文档](./troubleshooting.md)。

## 升级和维护

### 升级服务

```bash
# 1. 拉取新镜像
docker pull money-ocr-api:1.1.0

# 2. 停止旧容器
docker stop money-ocr
docker rm money-ocr

# 3. 启动新容器
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  money-ocr-api:1.1.0
```

### 备份和恢复

```bash
# 备份镜像
docker save money-ocr-api:1.0.0 -o backup.tar

# 恢复镜像
docker load -i backup.tar
```

## 安全建议

1. **网络安全**: 使用防火墙限制访问
2. **SSL/TLS**: 使用 HTTPS 保护数据传输
3. **认证**: 添加 API 认证机制
4. **资源限制**: 设置合理的资源限制
5. **日志审计**: 记录所有 API 访问日志

---

[返回文档首页](./README.md)
