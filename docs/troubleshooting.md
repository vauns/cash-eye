# 问题排查指南

本文档汇总常见问题和解决方案。

## 目录

- [安装问题](#安装问题)
- [模型加载问题](#模型加载问题)
- [API 使用问题](#api-使用问题)
- [Docker 部署问题](#docker-部署问题)
- [性能问题](#性能问题)
- [识别准确率问题](#识别准确率问题)
- [日志和调试](#日志和调试)

## 安装问题

### Q: pip install 失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案**:

```bash
# 1. 升级 pip
pip install --upgrade pip

# 2. 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 单独安装问题包
pip install paddleocr --upgrade
```

### Q: PaddlePaddle 安装失败

**症状**:
```
ERROR: No matching distribution found for paddlepaddle
```

**解决方案**:

```bash
# CPU 版本
pip install paddlepaddle

# GPU 版本（需要 CUDA）
pip install paddlepaddle-gpu

# 指定版本
pip install paddlepaddle==2.5.1
```

### Q: 缺少系统依赖

**症状**:
```
ImportError: libGL.so.1: cannot open shared object file
```

**解决方案**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libgl1 libglib2.0-0

# CentOS/RHEL
sudo yum install -y mesa-libGL glib2

# Alpine (Docker)
apk add --no-cache libgl libglib
```

## 模型加载问题

### Q: 模型下载失败

**症状**:
```
No available model hosting platforms detected.
Please check your network connection.
```

**原因**: 无法访问 HuggingFace、ModelScope 等模型托管平台。

**解决方案**:

**方案 1**: 配置网络访问
```bash
# 设置代理
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

**方案 2**: 手动下载模型
```bash
# 使用项目提供的脚本
python scripts/download_models.py --model-dir ./models

# 从国内镜像下载
python scripts/download_models.py --mirror modelscope
```

**方案 3**: 使用离线部署
参考 [部署指南 - 离线部署](./deployment.md#离线环境部署)

### Q: 模型文件损坏

**症状**:
```
Error loading model: Invalid model file
```

**解决方案**:

```bash
# 删除缓存
rm -rf ~/.paddleocr/

# 重新下载
python scripts/download_models.py
```

### Q: 模型加载超时

**症状**:
服务启动超过 2 分钟仍未就绪

**解决方案**:

```bash
# 检查模型是否存在
ls -la ~/.paddleocr/

# 查看日志
docker logs money-ocr 2>&1 | grep -i "model"

# 增加启动超时
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  --health-start-period=120s \
  money-ocr-api:1.0.0
```

## API 使用问题

### Q: 连接被拒绝

**症状**:
```
requests.exceptions.ConnectionError: Connection refused
```

**解决方案**:

```bash
# 1. 检查服务是否运行
docker ps | grep money-ocr
curl http://localhost:8000/api/v1/health

# 2. 检查端口映射
docker port money-ocr

# 3. 检查防火墙
sudo ufw status
sudo iptables -L
```

### Q: 请求超时

**症状**:
```
requests.exceptions.Timeout: Read timed out
```

**解决方案**:

```python
# 增加超时时间
response = requests.post(
    url,
    files=files,
    timeout=30  # 增加到 30 秒
)
```

### Q: 文件上传失败

**症状**:
```
{"error": {"code": "NO_FILE_PROVIDED", "message": "No file provided"}}
```

**解决方案**:

```python
# 正确的文件上传方式
with open("image.jpg", "rb") as f:
    files = {"file": f}  # 注意键名必须是 "file"
    response = requests.post(url, files=files)

# 或使用元组指定文件名
files = {"file": ("image.jpg", open("image.jpg", "rb"), "image/jpeg")}
```

### Q: 不支持的文件格式

**症状**:
```
{"error": {"code": "INVALID_FILE_FORMAT", "message": "Unsupported format"}}
```

**解决方案**:

支持的格式：JPEG, PNG, BMP, TIFF

```python
from PIL import Image

# 转换格式
img = Image.open("image.webp")
img.save("image.jpg", "JPEG")
```

### Q: 文件过大

**症状**:
```
{"error": {"code": "FILE_TOO_LARGE", "message": "File size exceeds limit"}}
```

**解决方案**:

```python
from PIL import Image

def compress_image(input_path, output_path, max_size_mb=1):
    """压缩图片到指定大小以下"""
    img = Image.open(input_path)
    quality = 85

    while True:
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        size_mb = os.path.getsize(output_path) / 1024 / 1024

        if size_mb <= max_size_mb or quality <= 20:
            break

        quality -= 5

    return output_path

# 使用
compress_image("large.jpg", "compressed.jpg", max_size_mb=1)
```

## Docker 部署问题

### Q: 容器启动后立即退出

**症状**:
```bash
$ docker ps
# 容器不在列表中
```

**解决方案**:

```bash
# 查看退出的容器
docker ps -a | grep money-ocr

# 查看日志
docker logs money-ocr

# 常见原因和解决：
# 1. 端口被占用
lsof -i :8000
sudo kill -9 <PID>

# 2. 权限问题
docker run -d --name money-ocr \
  --user $(id -u):$(id -g) \
  -p 8000:8000 \
  money-ocr-api:1.0.0

# 3. 资源不足
docker run -d --name money-ocr \
  -p 8000:8000 \
  --memory="2g" \
  money-ocr-api:1.0.0
```

### Q: 镜像构建失败

**症状**:
```
ERROR [stage-X Y/Z] RUN pip install...
```

**解决方案**:

```bash
# 1. 清理 Docker 缓存
docker builder prune -a

# 2. 使用国内镜像
# 编辑 Dockerfile，添加：
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 增加构建内存
docker build --memory=4g -t money-ocr-api:1.0.0 .
```

### Q: 无法访问容器服务

**症状**:
容器运行正常，但无法访问 http://localhost:8000

**解决方案**:

```bash
# 1. 检查端口映射
docker port money-ocr

# 2. 检查容器网络
docker inspect money-ocr | grep IPAddress

# 3. 尝试使用容器 IP
curl http://<container-ip>:8000/api/v1/health

# 4. 检查主机防火墙
sudo ufw allow 8000/tcp

# 5. 使用 host 网络模式
docker run -d --name money-ocr \
  --network host \
  money-ocr-api:1.0.0
```

## 性能问题

### Q: 响应时间过长

**症状**:
单次识别超过 10 秒

**解决方案**:

```bash
# 1. 检查图片大小
ls -lh image.jpg
# 如果 > 2MB，先压缩

# 2. 检查资源使用
docker stats money-ocr

# 3. 增加资源配置
docker update --memory="4g" --cpus="4" money-ocr

# 4. 查看是否有并发请求
docker logs money-ocr | grep "processing"

# 5. 优化图片
python -c "
from PIL import Image
img = Image.open('image.jpg')
img.thumbnail((2048, 2048))
img.save('optimized.jpg', 'JPEG', quality=85)
"
```

### Q: 内存占用过高

**症状**:
容器内存持续增长，超过 2GB

**解决方案**:

```bash
# 1. 重启容器（临时）
docker restart money-ocr

# 2. 设置内存限制
docker update --memory="2g" --memory-swap="2g" money-ocr

# 3. 检查是否有内存泄漏
docker logs money-ocr | grep -i "memory"

# 4. 启用自动重启
docker update --restart=on-failure:3 money-ocr

# 5. 监控内存趋势
watch -n 5 'docker stats money-ocr --no-stream'
```

### Q: CPU 使用率 100%

**症状**:
CPU 持续满载

**解决方案**:

```bash
# 1. 检查并发请求数
docker logs money-ocr --tail 100 | grep "POST"

# 2. 限制 CPU 使用
docker update --cpus="2.0" money-ocr

# 3. 检查是否有死循环
docker exec money-ocr ps aux

# 4. 减少并发
# 在客户端限制并发数为 5
```

## 识别准确率问题

### Q: 识别结果不准确

**可能原因和解决方案**:

**1. 图片质量差**
```python
# 提高图片质量
from PIL import Image, ImageEnhance

img = Image.open("blurry.jpg")

# 增强对比度
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.5)

# 增强锐度
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(2.0)

img.save("enhanced.jpg")
```

**2. 图片过大或过小**
```python
# 调整到最佳尺寸
img = Image.open("invoice.jpg")
# 推荐宽度 1000-2000 像素
if img.width < 1000:
    scale = 1000 / img.width
    new_size = (int(img.width * scale), int(img.height * scale))
    img = img.resize(new_size, Image.LANCZOS)
img.save("resized.jpg")
```

**3. 背景复杂**
```python
# 裁剪到金额区域
img = Image.open("invoice.jpg")
# 假设金额在右下角
width, height = img.size
crop_box = (width-500, height-200, width, height)
cropped = img.crop(crop_box)
cropped.save("amount_only.jpg")
```

**4. 字体特殊**
- 尝试使用更清晰的图片
- 转换为标准字体后再拍照
- 考虑使用更大的模型

### Q: 置信度过低

**症状**:
`confidence < 0.8`

**解决方案**:

```python
# 1. 人工复核低置信度结果
if result["confidence"] < 0.8:
    print(f"警告：置信度较低 ({result['confidence']:.2f})")
    print(f"原始文本: {result['raw_text']}")
    # 提示人工确认

# 2. 多次识别取平均
results = []
for _ in range(3):
    r = recognize_amount("invoice.jpg")
    results.append(r)

# 选择置信度最高的
best = max(results, key=lambda x: x['confidence'])
```

### Q: 无法识别某些货币符号

**症状**:
￥ 或 $ 符号识别失败

**解决方案**:

目前支持的符号：¥, ￥, $, ¥, CNY, USD

```python
# 检查原始文本
result = recognize_amount("invoice.jpg")
print("原始文本:", result["raw_text"])

# 如果 raw_text 中有货币符号但 amount 为空
# 可能是符号不在支持列表中
# 解决方案：
# 1. 预处理去除特殊符号
# 2. 只识别数字部分
# 3. 提交 Issue 请求支持新符号
```

## 日志和调试

### 查看日志

```bash
# Docker 容器日志
docker logs money-ocr

# 实时日志
docker logs -f money-ocr

# 最近 100 行
docker logs --tail 100 money-ocr

# 带时间戳
docker logs -t money-ocr

# 只看错误
docker logs money-ocr 2>&1 | grep ERROR
```

### 调试模式

```bash
# 启用 DEBUG 日志
docker run -d \
  --name money-ocr \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  money-ocr-api:1.0.0

# 查看详细日志
docker logs -f money-ocr
```

### 进入容器调试

```bash
# 进入运行中的容器
docker exec -it money-ocr bash

# 在容器内检查
python --version
pip list | grep paddle
ls -la ~/.paddleocr/
ps aux
df -h
```

### 本地调试

```bash
# 本地运行（不使用 Docker）
export LOG_LEVEL=DEBUG
python -m uvicorn main:app --reload --log-level debug

# 使用 pdb 调试
python -m pdb main.py
```

## 获取帮助

如果以上方案都无法解决问题：

1. **查看完整日志**:
   ```bash
   docker logs money-ocr > logs.txt
   ```

2. **收集系统信息**:
   ```bash
   docker version
   docker info
   uname -a
   free -h
   df -h
   ```

3. **提交 Issue**:
   - 访问: https://github.com/your-org/cash-eye/issues
   - 提供：错误日志、系统信息、复现步骤

4. **联系维护者**:
   - Email: support@example.com
   - 钉钉/企业微信群

## 常用诊断命令

```bash
# 检查服务状态
curl http://localhost:8000/api/v1/health

# 检查容器状态
docker ps -a | grep money-ocr

# 检查资源使用
docker stats money-ocr --no-stream

# 检查网络连接
nc -zv localhost 8000

# 检查端口占用
lsof -i :8000
netstat -tlnp | grep 8000

# 检查磁盘空间
df -h

# 检查内存使用
free -h

# 检查进程
docker exec money-ocr ps aux

# 检查模型文件
docker exec money-ocr ls -la /root/.paddleocr/
```

---

[返回文档首页](./README.md)
