# 多阶段构建 - 优化镜像大小
FROM python:3.10-slim AS builder

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# 最终运行镜像
FROM python:3.10-slim

WORKDIR /app

# 安装PaddleOCR依赖的系统库
# 注意: Debian 12+ 中 libgl1-mesa-glx 已被 libgl1 取代
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制Python包
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY src/ ./src/
COPY main.py .

# 构建参数：控制是否包含离线模型
ARG OFFLINE_BUILD=false

# 【离线部署】如果 OFFLINE_BUILD=true，复制预下载的模型文件
# 使用方法：docker build --build-arg OFFLINE_BUILD=true -t money-ocr-api:1.0.0 .
#
# 准备模型的方法：
#   方法1: bash scripts/prepare_deployment.sh
#   方法2: python scripts/download_models.py --model-dir ./models
COPY models/ /tmp/models/ 2>/dev/null || true
RUN if [ "$OFFLINE_BUILD" = "true" ] && [ -d "/tmp/models" ]; then \
        echo "📦 包含离线模型到镜像中..." && \
        mkdir -p /root/.paddlex/official_models && \
        cp -r /tmp/models/* /root/.paddlex/official_models/ 2>/dev/null || true && \
        rm -rf /tmp/models && \
        echo "✅ 离线模型已包含"; \
    else \
        echo "🌐 在线模式：运行时从网络下载模型" && \
        rm -rf /tmp/models; \
    fi

# 确保Python能找到用户安装的包
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# 配置环境变量
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV MAX_FILE_SIZE_MB=10

# 【离线部署】模型缓存目录
ENV PADDLE_HOME=/root/.paddlex
ENV HUB_HOME=/root/.paddlex

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
