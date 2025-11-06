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
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制Python包
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY src/ ./src/
COPY main.py .

# 确保Python能找到用户安装的包
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# 配置环境变量
ENV PORT=8000
ENV LOG_LEVEL=INFO
ENV MAX_FILE_SIZE_MB=10

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
