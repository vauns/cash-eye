# Windows 环境使用指南

本文档说明如何在 Windows 环境中进行离线部署准备。

## 系统要求

- Windows 10/11
- Python 3.10+
- Docker Desktop for Windows（用于构建镜像）
- PowerShell 或 命令提示符

## 快速开始

### 方法一：使用批处理脚本（推荐）

#### 1. 下载模型

使用命令提示符或 PowerShell：

```cmd
cd D:\PycharmProjects\MoneyOCR

# 下载到默认目录
scripts\download_models.bat

# 或下载到指定目录
scripts\download_models.bat models
```

#### 2. 准备离线部署（一键完成）

```cmd
# 下载并打包模型
scripts\prepare_offline_deployment.bat
```

这个脚本会：
- 创建 `models` 目录
- 下载 PaddleOCR 模型
- 打包为 `paddleocr-models-offline.tar.gz`（如果系统支持 tar 命令）

#### 3. 构建离线镜像

```cmd
# 构建 Docker 镜像
scripts\build_offline_image.bat
```

### 方法二：直接使用 Python 脚本

如果批处理脚本出现问题，可以直接使用 Python 脚本：

```cmd
# 激活虚拟环境（如果使用）
.venv\Scripts\activate

# 下载模型
python scripts\download_models.py --model-dir models

# 验证模型下载
dir models /s
```

## 常见问题

### Q1: "用提供的模式无法找到文件" 错误

**原因：**
- 在 Windows 上尝试运行 `.sh` 脚本
- 路径分隔符问题（`/` vs `\`）
- 使用了 Linux 风格的命令

**解决方案：**

✅ **使用批处理脚本**
```cmd
scripts\download_models.bat
```

❌ **不要这样使用**
```cmd
bash scripts/download_models.sh  # 需要 Git Bash 或 WSL
```

### Q2: 没有安装 Git Bash 或 WSL

如果你的系统没有 Git Bash 或 WSL（Windows Subsystem for Linux），使用提供的 `.bat` 批处理脚本即可。

### Q3: tar 命令未找到

Windows 10 1803+ 自带 `tar` 命令。如果提示未找到：

**选项 1：手动压缩**
```cmd
# 下载模型
python scripts\download_models.py --model-dir models

# 使用 Windows 资源管理器右键压缩 models 文件夹
# 或使用 7-Zip、WinRAR 等工具
```

**选项 2：使用 PowerShell 压缩**
```powershell
# 压缩模型目录
Compress-Archive -Path models\* -DestinationPath paddleocr-models-offline.zip
```

### Q4: Docker 构建失败

**检查事项：**
1. Docker Desktop 是否运行
2. 是否切换到 Linux 容器模式（默认）
3. 模型文件是否存在

```cmd
# 检查 Docker
docker version

# 检查模型目录
dir models

# 手动构建
docker build -f Dockerfile.offline -t money-ocr-api:offline .
```

## PowerShell 替代命令

如果你更喜欢使用 PowerShell：

### 下载模型

```powershell
# 下载到默认目录
python scripts/download_models.py

# 下载到指定目录
python scripts/download_models.py --model-dir "./models"
```

### 检查模型文件

```powershell
# 列出所有模型文件
Get-ChildItem -Path models -Recurse -File

# 计算总大小
$size = (Get-ChildItem -Path models -Recurse -File | Measure-Object -Property Length -Sum).Sum
"{0:N2} MB" -f ($size / 1MB)
```

### 压缩模型目录

```powershell
# 创建 ZIP 压缩包
Compress-Archive -Path models\* -DestinationPath paddleocr-models-offline.zip -Force

# 查看压缩包大小
(Get-Item paddleocr-models-offline.zip).Length / 1MB
```

### 构建 Docker 镜像

```powershell
# 构建镜像
docker build -f Dockerfile.offline -t money-ocr-api:offline .

# 导出镜像
docker save money-ocr-api:offline -o money-ocr-api-offline.tar

# 查看镜像大小
docker images money-ocr-api:offline
```

## 路径问题处理

### Windows 路径格式

在 Windows 上，使用以下路径格式：

```cmd
# 命令提示符
scripts\download_models.py
D:\Projects\MoneyOCR\models

# PowerShell（支持两种）
scripts\download_models.py
scripts/download_models.py
```

### Python 脚本中的路径

Python 脚本会自动处理路径分隔符，无需特殊处理：

```python
# 这在 Windows 和 Linux 上都可以工作
python scripts/download_models.py --model-dir ./models
python scripts/download_models.py --model-dir .\models
```

## Docker Desktop 设置

### 资源配置

打开 Docker Desktop -> Settings -> Resources：

```
CPU: 2 核心以上
内存: 4GB 以上（构建镜像时需要）
磁盘: 10GB 可用空间
```

### 切换容器模式

确保使用 Linux 容器（默认）：

1. 右键 Docker Desktop 托盘图标
2. 如果看到 "Switch to Linux containers..."，点击切换
3. 如果看到 "Switch to Windows containers..."，说明已经是 Linux 模式

## Git Bash 用户

如果你安装了 Git for Windows，可以使用 Git Bash 运行 `.sh` 脚本：

```bash
# 在 Git Bash 中
bash scripts/prepare_offline_deployment.sh
bash scripts/build_offline_image.sh
```

**注意：** 路径需要使用 Unix 风格 (`/`)：
```bash
python scripts/download_models.py --model-dir ./models
```

## WSL (Windows Subsystem for Linux) 用户

如果安装了 WSL，可以在 WSL 终端中使用 Linux 命令：

```bash
# 在 WSL 终端中
cd /mnt/d/PycharmProjects/MoneyOCR

# 使用 bash 脚本
bash scripts/prepare_offline_deployment.sh
bash scripts/build_offline_image.sh
```

## 完整示例：从头到尾

### 场景：在 Windows 上准备离线部署包

```cmd
REM 1. 打开命令提示符，进入项目目录
cd D:\PycharmProjects\MoneyOCR

REM 2. 激活虚拟环境（如果使用）
.venv\Scripts\activate

REM 3. 下载模型
python scripts\download_models.py --model-dir models

REM 4. 验证模型下载成功
dir models /s

REM 5. 构建 Docker 镜像
docker build -f Dockerfile.offline -t money-ocr-api:offline .

REM 6. 导出镜像
docker save money-ocr-api:offline -o money-ocr-api-offline.tar

REM 7. 检查导出文件
dir money-ocr-api-offline.tar

REM 完成！将 money-ocr-api-offline.tar 复制到离线环境即可
```

## 文件编码问题

如果批处理脚本出现乱码，确保文件编码为 ANSI 或 UTF-8 with BOM：

1. 使用记事本打开 `.bat` 文件
2. 另存为 -> 编码选择 "ANSI"
3. 保存并重新运行

## 获取帮助

如果遇到问题：

1. **查看错误信息**
   ```cmd
   # 将错误输出保存到文件
   python scripts\download_models.py --model-dir models > output.log 2>&1
   type output.log
   ```

2. **检查 Python 环境**
   ```cmd
   python --version
   pip list | findstr paddleocr
   ```

3. **检查 Docker 状态**
   ```cmd
   docker info
   docker ps
   ```

4. **查看详细日志**
   ```cmd
   # Python 脚本会输出详细日志
   python scripts\download_models.py --model-dir models
   ```

---

**相关文档：**
- [离线部署指南](./OFFLINE_DEPLOYMENT.md) - 完整的离线部署方案
- [README.md](./README.md) - 项目主文档
