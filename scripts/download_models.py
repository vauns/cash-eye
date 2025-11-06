#!/usr/bin/env python3
"""
模型预下载脚本

用于在有网络的环境中预先下载 PaddleOCR 模型文件。
下载的模型可以打包到 Docker 镜像中，或通过卷挂载方式用于离线部署。
"""

import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_models(model_dir: str = None):
    """
    下载 PaddleOCR 模型文件

    Args:
        model_dir: 模型保存目录，默认为 ~/.paddlex/
    """
    try:
        from paddleocr import TextDetection, TextRecognition

        # 设置模型保存目录
        # 注意: PaddleOCR 3.3.1+ 使用 PADDLE_HOME 环境变量
        if model_dir:
            model_dir = os.path.abspath(model_dir)
            os.makedirs(model_dir, exist_ok=True)
            # 设置多个可能的环境变量，确保兼容性
            os.environ['PADDLE_HOME'] = model_dir
            os.environ['HUB_HOME'] = model_dir
            logger.info(f"模型将保存到: {model_dir}")
            logger.info(f"设置环境变量 PADDLE_HOME={model_dir}")
        else:
            # PaddleOCR 3.3.1+ 默认使用 ~/.paddlex/
            default_dir = os.path.expanduser("~/.paddlex")
            logger.info(f"模型将保存到默认目录: {default_dir}")

        logger.info("=" * 60)
        logger.info("开始下载 PP-OCRv5_mobile_det 检测模型...")
        logger.info("=" * 60)

        # 初始化文本检测模型（会自动下载）
        # 注意：PaddleOCR 会在控制台输出下载进度
        detector = TextDetection(
            model_name='PP-OCRv5_mobile_det'
        )
        logger.info("✓ 检测模型下载完成")

        logger.info("=" * 60)
        logger.info("开始下载 PP-OCRv5_mobile_rec 识别模型...")
        logger.info("=" * 60)

        # 初始化文本识别模型（会自动下载）
        # 注意：PaddleOCR 会在控制台输出下载进度
        recognizer = TextRecognition(
            model_name='PP-OCRv5_mobile_rec'
        )
        logger.info("✓ 识别模型下载完成")

        logger.info("=" * 60)
        logger.info("所有模型下载完成！")
        logger.info("=" * 60)

        # 显示模型文件位置
        # 检查多个可能的路径
        possible_paths = []
        if model_dir:
            possible_paths.append(Path(model_dir))

        # 添加默认路径
        possible_paths.extend([
            Path.home() / ".paddlex",
            Path.home() / ".paddleocr"
        ])

        logger.info("\n" + "=" * 60)
        logger.info("检查模型文件位置...")
        logger.info("=" * 60)

        found_models = False
        for model_path in possible_paths:
            if model_path.exists() and any(model_path.rglob("*.pdmodel")):
                logger.info(f"\n✓ 找到模型文件: {model_path}")

                # 列出模型目录
                model_dirs = [d for d in model_path.rglob("PP-OCRv5*") if d.is_dir()]
                if model_dirs:
                    logger.info("模型列表:")
                    for model_dir_path in model_dirs:
                        size = sum(f.stat().st_size for f in model_dir_path.rglob("*") if f.is_file())
                        size_mb = size / (1024 * 1024)
                        logger.info(f"  - {model_dir_path.name} ({size_mb:.2f} MB)")

                # 计算总大小
                total_size = sum(f.stat().st_size for f in model_path.rglob("*") if f.is_file())
                total_size_mb = total_size / (1024 * 1024)
                logger.info(f"\n总大小: {total_size_mb:.2f} MB")

                found_models = True

        if not found_models:
            logger.warning("\n警告: 未找到已下载的模型文件")
            logger.warning("模型可能已下载但位于其他位置")

        return True

    except ImportError as e:
        logger.error("导入错误：请确保已安装 PaddleOCR")
        logger.error(f"错误详情: {e}")
        logger.error("\n安装命令: pip install paddleocr==3.3.1")
        return False

    except Exception as e:
        logger.error(f"下载模型时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="PaddleOCR 模型预下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 下载到默认目录 (~/.paddleocr/)
  python scripts/download_models.py

  # 下载到指定目录
  python scripts/download_models.py --model-dir ./models

  # 在 Docker 构建时使用
  python scripts/download_models.py --model-dir /app/.paddleocr
"""
    )

    parser.add_argument(
        '--model-dir',
        type=str,
        help='模型保存目录（默认: ~/.paddleocr/）'
    )

    args = parser.parse_args()

    logger.info("PaddleOCR 模型下载工具")
    logger.info("=" * 60)

    success = download_models(args.model_dir)

    if success:
        logger.info("\n✓ 模型下载成功！")
        logger.info("\n后续步骤:")
        logger.info("1. 如需离线部署，请将模型目录打包")
        logger.info("2. 在离线环境解压到相同路径")
        logger.info("3. 或修改 Dockerfile 将模型复制到镜像中")
        sys.exit(0)
    else:
        logger.error("\n✗ 模型下载失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
