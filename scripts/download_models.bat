@echo off
REM Windows 批处理脚本 - 下载 PaddleOCR 模型
REM 用法: download_models.bat [模型目录]

setlocal enabledelayedexpansion

echo ==========================================
echo PaddleOCR 模型下载工具 (Windows)
echo ==========================================
echo.

REM 检查是否提供了模型目录参数
if "%~1"=="" (
    echo 下载到默认目录: %%USERPROFILE%%\.paddleocr
    python scripts\download_models.py
) else (
    echo 下载到指定目录: %~1
    python scripts\download_models.py --model-dir "%~1"
)

if errorlevel 1 (
    echo.
    echo [错误] 模型下载失败
    exit /b 1
)

echo.
echo ==========================================
echo 模型下载成功！
echo ==========================================
echo.

pause
