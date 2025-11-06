#!/bin/bash
# 构建 Docker 镜像脚本
#
# 此脚本会：
# 1. 检查模型文件是否存在
# 2. 构建包含模型的 Docker 镜像
# 3. （可选）导出镜像为 tar 文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="${PROJECT_ROOT}/models"
IMAGE_NAME="money-ocr-api"
IMAGE_TAG="1.0.0"
EXPORT_TAR="money-ocr-api.tar"

echo "=========================================="
echo "PaddleOCR 镜像构建工具"
echo "=========================================="
echo ""

# 检查模型目录是否存在
if [ ! -d "${MODEL_DIR}" ]; then
    echo "错误：模型目录不存在: ${MODEL_DIR}"
    echo ""
    echo "请先运行以下命令下载模型："
    echo "  bash scripts/prepare_deployment.sh"
    exit 1
fi

# 检查模型文件
MODEL_COUNT=$(find "${MODEL_DIR}" -type f | wc -l)
if [ "${MODEL_COUNT}" -eq 0 ]; then
    echo "错误：模型目录为空: ${MODEL_DIR}"
    echo ""
    echo "请先运行以下命令下载模型："
    echo "  bash scripts/prepare_deployment.sh"
    exit 1
fi

echo "✓ 检测到模型文件: ${MODEL_COUNT} 个"
echo ""

# 显示模型目录大小
MODEL_SIZE=$(du -sh "${MODEL_DIR}" | cut -f1)
echo "模型目录大小: ${MODEL_SIZE}"
echo ""

# 构建镜像
echo "开始构建 Docker 镜像..."
echo "  镜像名称: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Dockerfile: Dockerfile"
echo "  构建模式: 包含预下载模型（OFFLINE_BUILD=true）"
echo ""

cd "${PROJECT_ROOT}"

# 临时替换 .dockerignore（如果需要）
if [ -f .dockerignore ]; then
    if grep -q "^models/" .dockerignore 2>/dev/null; then
        echo "注意：.dockerignore 中包含 models/ 规则，创建临时配置..."
        cp .dockerignore .dockerignore.backup
        grep -v "^models/" .dockerignore > .dockerignore.tmp
        mv .dockerignore.tmp .dockerignore
        RESTORE_DOCKERIGNORE=true
    fi
fi

# 构建镜像（启用离线模式，将模型打包到镜像中）
docker build --build-arg OFFLINE_BUILD=true -t "${IMAGE_NAME}:${IMAGE_TAG}" .

BUILD_STATUS=$?

# 恢复 .dockerignore
if [ "${RESTORE_DOCKERIGNORE}" = true ]; then
    echo "恢复 .dockerignore..."
    mv .dockerignore.backup .dockerignore
fi

if [ ${BUILD_STATUS} -ne 0 ]; then
    echo ""
    echo "错误：Docker 镜像构建失败"
    exit 1
fi

echo ""
echo "✓ Docker 镜像构建成功！"
echo ""

# 显示镜像信息
IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.Size}}")
echo "镜像信息："
echo "  名称: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  大小: ${IMAGE_SIZE}"
echo ""

# 询问是否导出镜像
read -p "是否导出镜像为 tar 文件？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "正在导出镜像..."
    docker save "${IMAGE_NAME}:${IMAGE_TAG}" -o "${EXPORT_TAR}"

    if [ $? -eq 0 ]; then
        TAR_SIZE=$(du -h "${EXPORT_TAR}" | cut -f1)
        echo "✓ 镜像已导出: ${EXPORT_TAR} (${TAR_SIZE})"
        echo ""
        echo "在离线环境加载镜像："
        echo "  docker load -i ${EXPORT_TAR}"
    else
        echo "错误：镜像导出失败"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "✓ 镜像构建完成！"
echo "=========================================="
echo ""
echo "后续步骤："
echo ""
echo "1. 测试镜像："
echo "   docker run -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "2. 使用 docker-compose 启动："
echo "   docker-compose up -d"
echo ""
echo "3. 部署到离线环境："
echo "   a. 导出镜像: docker save ${IMAGE_NAME}:${IMAGE_TAG} -o ${EXPORT_TAR}"
echo "   b. 复制到离线服务器"
echo "   c. 加载镜像: docker load -i ${EXPORT_TAR}"
echo "   d. 启动容器: docker run -d --name money-ocr -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

