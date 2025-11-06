@echo off
REM Windows 批处理脚本 - 构建离线 Docker 镜像
REM
REM 此脚本会：
REM 1. 检查模型文件是否存在
REM 2. 构建包含模型的 Docker 镜像
REM 3. （可选）导出镜像为 tar 文件

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set MODEL_DIR=%PROJECT_ROOT%\models
set IMAGE_NAME=money-ocr-api
set IMAGE_TAG=offline
set EXPORT_TAR=money-ocr-api-offline.tar

echo ==========================================
echo PaddleOCR 离线镜像构建工具 (Windows)
echo ==========================================
echo.

REM 检查模型目录是否存在
if not exist "%MODEL_DIR%" (
    echo [错误] 模型目录不存在: %MODEL_DIR%
    echo.
    echo 请先运行以下命令下载模型：
    echo   scripts\prepare_offline_deployment.bat
    pause
    exit /b 1
)

REM 检查模型文件
set MODEL_COUNT=0
for /r "%MODEL_DIR%" %%F in (*) do set /a MODEL_COUNT+=1

if !MODEL_COUNT! equ 0 (
    echo [错误] 模型目录为空: %MODEL_DIR%
    echo.
    echo 请先运行以下命令下载模型：
    echo   scripts\prepare_offline_deployment.bat
    pause
    exit /b 1
)

echo [✓] 检测到模型文件: !MODEL_COUNT! 个
echo.

REM 构建镜像
echo 开始构建 Docker 镜像...
echo   镜像名称: %IMAGE_NAME%:%IMAGE_TAG%
echo   Dockerfile: Dockerfile.offline
echo.

cd /d "%PROJECT_ROOT%"
docker build -f Dockerfile.offline -t %IMAGE_NAME%:%IMAGE_TAG% .

if errorlevel 1 (
    echo.
    echo [错误] Docker 镜像构建失败
    pause
    exit /b 1
)

echo.
echo [✓] Docker 镜像构建成功！
echo.

REM 显示镜像信息
for /f "tokens=*" %%i in ('docker images %IMAGE_NAME%:%IMAGE_TAG% --format "{{.Size}}"') do set IMAGE_SIZE=%%i
echo 镜像信息：
echo   名称: %IMAGE_NAME%:%IMAGE_TAG%
echo   大小: !IMAGE_SIZE!
echo.

REM 询问是否导出镜像
set /p EXPORT_CHOICE="是否导出镜像为 tar 文件？(Y/N) "
if /i "!EXPORT_CHOICE!"=="Y" (
    echo.
    echo 正在导出镜像...
    docker save %IMAGE_NAME%:%IMAGE_TAG% -o "%EXPORT_TAR%"

    if errorlevel 1 (
        echo [错误] 镜像导出失败
        pause
        exit /b 1
    )

    for %%A in ("%EXPORT_TAR%") do set TAR_SIZE_BYTES=%%~zA
    set /a TAR_SIZE_MB=!TAR_SIZE_BYTES! / 1048576
    echo [✓] 镜像已导出: %EXPORT_TAR% (!TAR_SIZE_MB! MB^)
    echo.
    echo 在离线环境加载镜像：
    echo   docker load -i %EXPORT_TAR%
)

echo.
echo ==========================================
echo [✓] 离线镜像构建完成！
echo ==========================================
echo.
echo 后续步骤：
echo.
echo 1. 测试镜像：
echo    docker run -p 8000:8000 %IMAGE_NAME%:%IMAGE_TAG%
echo.
echo 2. 使用 docker-compose 启动：
echo    docker-compose -f docker-compose.offline.yml up -d
echo.
echo 3. 部署到离线环境：
echo    a. 导出镜像: docker save %IMAGE_NAME%:%IMAGE_TAG% -o %EXPORT_TAR%
echo    b. 复制到离线服务器
echo    c. 加载镜像: docker load -i %EXPORT_TAR%
echo    d. 启动容器: docker-compose -f docker-compose.offline.yml up -d
echo.

pause
