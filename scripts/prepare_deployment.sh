#!/bin/bash
# 部署准备脚本
#
# 此脚本用于在有网络的环境中准备部署所需的模型文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="${PROJECT_ROOT}/models"
PACKAGE_NAME="paddleocr-models.tar.gz"

echo "=========================================="
echo "PaddleOCR 部署准备工具"
echo "=========================================="
echo ""

# 创建模型目录
echo "1. 创建模型目录: ${MODEL_DIR}"
mkdir -p "${MODEL_DIR}"

# 下载模型
echo ""
echo "2. 下载 PaddleOCR 模型..."
python3 "${SCRIPT_DIR}/download_models.py" --model-dir "${MODEL_DIR}"

if [ $? -ne 0 ]; then
    echo "错误：模型下载失败"
    exit 1
fi

# 打包模型
echo ""
echo "3. 打包模型文件..."
cd "${PROJECT_ROOT}"
tar -czf "${PACKAGE_NAME}" -C models .

if [ $? -eq 0 ]; then
    PACKAGE_SIZE=$(du -h "${PACKAGE_NAME}" | cut -f1)
    echo "✓ 模型打包完成: ${PACKAGE_NAME} (${PACKAGE_SIZE})"
else
    echo "错误：模型打包失败"
    exit 1
fi

# 显示后续步骤
echo ""
echo "=========================================="
echo "✓ 部署准备完成！"
echo "=========================================="
echo ""
echo "后续步骤："
echo ""
echo "方案一：构建包含模型的 Docker 镜像"
echo "  1. 使用构建脚本："
echo "     bash scripts/build_image.sh"
echo "  2. 或手动构建："
echo "     docker build --build-arg OFFLINE_BUILD=true -t money-ocr-api:1.0.0 ."
echo ""
echo "方案二：使用卷挂载（推荐用于开发环境）"
echo "  1. 将 ${PACKAGE_NAME} 复制到离线环境"
echo "  2. 解压: mkdir -p models && tar -xzf ${PACKAGE_NAME} -C models"
echo "  3. 启动容器时挂载模型目录："
echo "     docker run -d -p 8000:8000 -v \$(pwd)/models:/root/.paddlex/official_models:ro money-ocr-api:1.0.0"
echo ""
echo "方案三：手动复制模型目录"
echo "  1. 将 ./models 目录复制到离线环境"
echo "  2. 在 Docker 容器中挂载或复制到 /root/.paddlex/official_models/"
echo ""
