#!/usr/bin/env python3
"""
模型复制工具

用于将已下载的 PaddleOCR 模型从默认位置复制到指定目录。
适用于模型已经存在于 ~/.paddlex/ 但需要移动到项目目录的情况。
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_model_directory():
    """查找已下载的模型目录"""
    possible_paths = [
        Path.home() / ".paddlex" / "official_models",
        Path.home() / ".paddleocr" / "whl",
        Path.home() / ".paddleocr",
    ]

    for path in possible_paths:
        if path.exists():
            # 检查是否包含 PP-OCRv5 模型
            models = list(path.rglob("PP-OCRv5*"))
            if models:
                logger.info(f"找到模型目录: {path}")
                return path

    return None


def copy_models(source_dir: Path, target_dir: str):
    """
    复制模型文件

    Args:
        source_dir: 源目录
        target_dir: 目标目录
    """
    target_path = Path(target_dir).absolute()
    target_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"源目录: {source_dir}")
    logger.info(f"目标目录: {target_path}")
    logger.info("")

    # 找到所有 PP-OCRv5 模型
    model_dirs = [d for d in source_dir.rglob("PP-OCRv5*") if d.is_dir()]

    if not model_dirs:
        logger.error("未找到 PP-OCRv5 模型")
        return False

    logger.info(f"找到 {len(model_dirs)} 个模型:")
    for model_dir in model_dirs:
        logger.info(f"  - {model_dir.name}")

    logger.info("")
    logger.info("开始复制...")

    copied_count = 0
    for model_dir in model_dirs:
        try:
            # 保持原有的目录结构
            relative_path = model_dir.relative_to(source_dir)
            dest = target_path / relative_path

            if dest.exists():
                logger.info(f"跳过 {model_dir.name} (已存在)")
                continue

            logger.info(f"复制 {model_dir.name}...")
            shutil.copytree(model_dir, dest)

            # 计算大小
            size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
            size_mb = size / (1024 * 1024)
            logger.info(f"  ✓ 完成 ({size_mb:.2f} MB)")

            copied_count += 1

        except Exception as e:
            logger.error(f"  ✗ 复制失败: {e}")

    logger.info("")
    logger.info(f"复制完成: {copied_count}/{len(model_dirs)} 个模型")

    # 计算总大小
    if target_path.exists():
        total_size = sum(f.stat().st_size for f in target_path.rglob("*") if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        logger.info(f"目标目录总大小: {total_size_mb:.2f} MB")

    return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="PaddleOCR 模型复制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 自动查找并复制到指定目录
  python scripts/copy_models.py --target-dir ./models

  # 指定源目录和目标目录
  python scripts/copy_models.py --source-dir ~/.paddlex/official_models --target-dir ./models

常见场景:
  1. 模型已下载到 C:\\Users\\username\\.paddlex\\official_models
  2. 需要复制到项目目录 ./models 用于 Docker 构建
  3. 运行此脚本自动复制
"""
    )

    parser.add_argument(
        '--source-dir',
        type=str,
        help='源目录（如不指定则自动查找）'
    )

    parser.add_argument(
        '--target-dir',
        type=str,
        required=True,
        help='目标目录（必需）'
    )

    args = parser.parse_args()

    logger.info("PaddleOCR 模型复制工具")
    logger.info("=" * 60)
    logger.info("")

    # 查找源目录
    if args.source_dir:
        source_dir = Path(args.source_dir).absolute()
        if not source_dir.exists():
            logger.error(f"源目录不存在: {source_dir}")
            sys.exit(1)
    else:
        logger.info("正在查找已下载的模型...")
        source_dir = find_model_directory()
        if not source_dir:
            logger.error("未找到已下载的模型")
            logger.error("")
            logger.error("请先下载模型:")
            logger.error("  python scripts/download_models.py")
            logger.error("")
            logger.error("或手动指定源目录:")
            logger.error("  python scripts/copy_models.py --source-dir <path> --target-dir ./models")
            sys.exit(1)

    logger.info("")

    # 复制模型
    success = copy_models(source_dir, args.target_dir)

    if success:
        logger.info("")
        logger.info("=" * 60)
        logger.info("✓ 模型复制成功！")
        logger.info("=" * 60)
        logger.info("")
        logger.info("后续步骤:")
        logger.info("1. 构建 Docker 镜像:")
        logger.info("   docker build --build-arg OFFLINE_BUILD=true -t money-ocr-api:1.0.0 .")
        logger.info("")
        logger.info("2. 或使用构建脚本:")
        logger.info("   bash scripts/build_image.sh")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("✗ 模型复制失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
