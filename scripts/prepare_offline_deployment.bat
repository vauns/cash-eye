@echo off
REM Windows 批处理脚本 - 准备离线部署
REM 此脚本用于在有网络的环境中准备离线部署所需的模型文件

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set MODEL_DIR=%PROJECT_ROOT%\models
set PACKAGE_NAME=paddleocr-models-offline.tar.gz

echo ==========================================
echo PaddleOCR 离线部署准备工具 (Windows)
echo ==========================================
echo.

REM 创建模型目录
echo 1. 创建模型目录: %MODEL_DIR%
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

REM 下载模型
echo.
echo 2. 下载 PaddleOCR 模型...
python "%SCRIPT_DIR%download_models.py" --model-dir "%MODEL_DIR%"

if errorlevel 1 (
    echo [错误] 模型下载失败
    exit /b 1
)

REM 检查是否安装了 tar 命令 (Windows 10 1803+ 自带)
where tar >nul 2>nul
if errorlevel 1 (
    echo.
    echo [警告] 未找到 tar 命令，跳过打包步骤
    echo 请手动压缩 models 目录或使用 7-Zip 等工具
    goto :finish
)

REM 打包模型
echo.
echo 3. 打包模型文件...
cd /d "%PROJECT_ROOT%"
tar -czf "%PACKAGE_NAME%" -C models .

if errorlevel 1 (
    echo [错误] 模型打包失败
    exit /b 1
)

for %%A in ("%PACKAGE_NAME%") do set PACKAGE_SIZE=%%~zA
set /a PACKAGE_SIZE_MB=!PACKAGE_SIZE! / 1048576
echo 模型打包完成: %PACKAGE_NAME% (!PACKAGE_SIZE_MB! MB)

:finish
echo.
echo ==========================================
echo 离线部署准备完成！
echo ==========================================
echo.
echo 后续步骤：
echo.
echo 方案一：构建包含模型的 Docker 镜像
echo   1. 使用 Dockerfile.offline 构建镜像：
echo      docker build -f Dockerfile.offline -t money-ocr-api:offline .
echo.
echo 方案二：使用卷挂载（推荐用于开发环境）
echo   1. 将 models 目录复制到离线环境
echo   2. 使用 docker-compose.offline.yml 启动：
echo      docker-compose -f docker-compose.offline.yml up -d
echo.
echo 方案三：手动复制模型目录
echo   1. 将 models 目录复制到离线环境
echo   2. 在 Docker 容器中挂载或复制到 /root/.paddleocr/
echo.

pause
